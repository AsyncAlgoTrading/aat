import pandas as pd  # type: ignore
import json
from datetime import datetime
from json import JSONEncoder
from aat.config import Side
from aat.core import Order, Trade, Instrument, ExchangeType, Position


class _Serializer(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (Trade, Instrument, Position, ExchangeType)):
            return obj.toJson()
        elif isinstance(obj, datetime):
            return obj.timestamp()
        else:
            raise Exception('Unknown type: {} - {}'.format(type(obj), obj))


class Portfolio(object):
    '''The portfolio object keeps track of a collection of positions attributed
    to a collection of strategies'''

    def __init__(self):
        # Track prices over time
        self._prices = {}
        self._trades = {}

        # Track active positions by instrument
        self._active_positions_by_instrument = {}

        # Track active positions by strategy and instrument
        self._active_positions_by_strategy = {}

    # *****************
    # Manager Methods #
    # *****************
    def newPosition(self, trade, strategy):
        my_order: Order = trade.my_order
        if trade.instrument in self._active_positions_by_instrument and \
           strategy.name() in self._active_positions_by_strategy and \
           trade.instrument in self._active_positions_by_strategy[strategy.name()]:

            # update position
            cur_pos = self._active_positions_by_strategy[strategy.name()][trade.instrument]
            cur_pos.trades.append(trade)

            # TODO update notional/size/price etc
            prev_size: float = cur_pos.size
            prev_price: float = cur_pos.price
            prev_notional: float = prev_size * prev_price

            cur_pos.size = (cur_pos.size + (my_order.volume if my_order.side == Side.BUY else -1 * my_order.volume), trade.timestamp)

            if (prev_size >= 0 and cur_pos.size > prev_size) or (prev_size <= 0 and cur_pos.size < prev_size):  # type: ignore
                # increasing position size
                # update average price
                cur_pos.price = ((prev_notional + (my_order.volume * trade.price)) / cur_pos.size, trade.timestamp)

            elif (prev_size > 0 and cur_pos.size < 0) or (prev_size < 0 and cur_pos.size > 0):  # type: ignore
                # decreasing position size in one direction, increasing position size in other
                # update realized pnl
                pnl = (prev_size * (trade.price - prev_price))
                cur_pos.pnl = (cur_pos.pnl + pnl, trade.timestamp)  # update realized pnl with closing position

                # deduct from unrealized pnl
                cur_pos.unrealizedPnl = (cur_pos.unrealizedPnl - pnl, trade.timestamp)

                # update average price
                cur_pos.price = (trade.price, trade.timestamp)

            else:
                # decreasing position size
                # update realized pnl
                pnl = (prev_size * (trade.price - prev_price))
                cur_pos.pnl = (cur_pos.pnl + pnl, trade.timestamp)  # update realized pnl with closing position

                # deduct from unrealized pnl
                cur_pos.unrealizedPnl = (cur_pos.unrealizedPnl - pnl, trade.timestamp)

            # TODO close if side is 0?

        else:
            # If strategy has no positions yet, make a new dict
            if strategy.name() not in self._active_positions_by_strategy:
                self._active_positions_by_strategy[strategy.name()] = {}

            # if not tracking instrument yet, add
            if trade.instrument not in self._active_positions_by_instrument:
                self._active_positions_by_instrument[trade.instrument] = []

            # Map position in by strategy
            self._active_positions_by_strategy[strategy.name()][trade.instrument] = Position(price=trade.price,
                                                                                             size=trade.volume,
                                                                                             timestamp=trade.timestamp,
                                                                                             instrument=trade.instrument,
                                                                                             exchange=trade.exchange,
                                                                                             trades=[trade])

            # map a single position by instrument
            self._active_positions_by_instrument[trade.instrument].append(
                self._active_positions_by_strategy[strategy.name()][trade.instrument]
            )

    def onTrade(self, trade):
        if trade.instrument in self._active_positions_by_instrument:
            for pos in self._active_positions_by_instrument[trade.instrument]:
                pos.unrealizedPnl = (pos.size * (trade.price - pos.price), trade.timestamp)
                pos.pnl = (pos.pnl, trade.timestamp)
                pos.instrumentPrice = (trade.price, trade.timestamp)

        if trade.instrument not in self._prices:
            self._prices[trade.instrument] = [(trade.price, trade.timestamp)]
            self._trades[trade.instrument] = [trade]
        else:
            self._prices[trade.instrument].append((trade.price, trade.timestamp))
            self._trades[trade.instrument].append(trade)

    def onTraded(self, trade, strategy):
        self.newPosition(trade, strategy)

    # ******************
    # Strategy Methods #
    # ******************
    def positions(self, strategy, instrument: Instrument = None, exchange: ExchangeType = None):
        ret = {}

        for position in self._active_positions_by_strategy[strategy.name()].values():
            if instrument and position.instrument != instrument:
                # Skip if not asking for this instrument
                continue

            if exchange and position.exchange != exchange:
                # Skip if not asking for this exchange
                continue

            ret[position.instrument] = position
        return list(ret.values())

    def allPositions(self, instrument: Instrument = None, exchange: ExchangeType = None):
        ret = {}

        for position_list in self._active_positions_by_instrument.values():
            for position in position_list:

                if instrument and position.instrument != instrument:
                    # Skip if not asking for this instrument
                    continue

                if exchange and position.exchange != exchange:
                    # Skip if not asking for this exchange
                    continue

                if position.instrument not in ret:
                    ret[position.instrument] = position
                else:
                    ret[position.instrument] += position
        return list(ret.values())

    def priceHistory(self, instrument: Instrument = None):
        if instrument:
            return pd.DataFrame(self._prices[instrument], columns=[instrument.name, 'when'])
        return {i: pd.DataFrame(self._prices[i], columns=[i.name, 'when']) for i in self._prices}

    def _constructDf(self, dfs, drop_duplicates=True):
        # join along time axis
        if dfs:
            df = pd.concat(dfs, sort=True)
            df.sort_index(inplace=True)
            df = df.groupby(df.index).last()

            if drop_duplicates:
                df.drop_duplicates(inplace=True)

            df.fillna(method='ffill', inplace=True)
        else:
            df = pd.DataFrame()
        return df

    def getPnl(self, strategy):
        portfolio = []
        pnl_cols = []
        total_pnl_cols = []
        for position in self.positions(strategy):
            instrument = position.instrument

            #######
            # Pnl #
            #######
            total_pnl_col = 'pnl:{}'.format(instrument.name)
            unrealized_pnl_col = 'ur:{}'.format(instrument.name)
            pnl_cols.append(unrealized_pnl_col)
            unrealized_pnl_history = pd.DataFrame(position.unrealizedPnlHistory, columns=[unrealized_pnl_col, 'when'])
            unrealized_pnl_history.set_index('when', inplace=True)

            realized_pnl_col = 'r:{}'.format(instrument.name)
            pnl_cols.append(realized_pnl_col)
            realized_pnl_history = pd.DataFrame(position.pnlHistory, columns=[realized_pnl_col, 'when'])
            realized_pnl_history.set_index('when', inplace=True)

            unrealized_pnl_history[realized_pnl_col] = realized_pnl_history[realized_pnl_col]
            unrealized_pnl_history[total_pnl_col] = unrealized_pnl_history.sum(axis=1)
            total_pnl_cols.append(total_pnl_col)
            portfolio.append(unrealized_pnl_history)

        df_pnl = self._constructDf(portfolio, drop_duplicates=False)  # dont drop duplicates

        ################
        # calculations #
        ################
        # calculate total pnl
        df_pnl['alpha'] = df_pnl[[c for c in df_pnl.columns if c.startswith('pnl:')]].sum(axis=1)
        return df_pnl

    def getPnlAll(self):
        portfolio = []
        pnl_cols = []
        total_pnl_cols = []
        for position in self.allPositions():
            instrument = position.instrument

            #######
            # Pnl #
            #######
            total_pnl_col = 'pnl:{}'.format(instrument.name)
            unrealized_pnl_col = 'ur:{}'.format(instrument.name)
            pnl_cols.append(unrealized_pnl_col)
            unrealized_pnl_history = pd.DataFrame(position.unrealizedPnlHistory, columns=[unrealized_pnl_col, 'when'])
            unrealized_pnl_history.set_index('when', inplace=True)

            realized_pnl_col = 'r:{}'.format(instrument.name)
            pnl_cols.append(realized_pnl_col)
            realized_pnl_history = pd.DataFrame(position.pnlHistory, columns=[realized_pnl_col, 'when'])
            realized_pnl_history.set_index('when', inplace=True)

            unrealized_pnl_history[realized_pnl_col] = realized_pnl_history[realized_pnl_col]
            unrealized_pnl_history[total_pnl_col] = unrealized_pnl_history.sum(axis=1)
            total_pnl_cols.append(total_pnl_col)
            portfolio.append(unrealized_pnl_history)

        df_pnl = self._constructDf(portfolio, drop_duplicates=False)  # dont drop duplicates

        ################
        # calculations #
        ################
        # calculate total pnl
        df_pnl['alpha'] = df_pnl[[c for c in df_pnl.columns if c.startswith('pnl:')]].sum(axis=1)
        return df_pnl

    def getInstruments(self, strategy):
        raise NotImplementedError()

    def getPrice(self):
        portfolio = []
        price_cols = []
        for instrument, price_history in self.priceHistory().items():
            #########
            # Price #
            #########
            price_col = instrument.name
            price_cols.append(price_col)
            price_history.set_index('when', inplace=True)
            portfolio.append(price_history)
        return self._constructDf(portfolio)

    def getAssetPrice(self, strategy):
        portfolio = []
        price_cols = []
        for position in self.allPositions():
            instrument = position.instrument

            #########
            # Price #
            #########
            price_col = instrument.name
            price_cols.append(price_col)
            price_history = pd.DataFrame(position.instrumentPriceHistory, columns=[price_col, 'when'])
            price_history.set_index('when', inplace=True)
            portfolio.append(price_history)
        return self._constructDf(portfolio)

    def getSize(self, strategy):
        portfolio = []
        size_cols = []
        for position in self.positions(strategy):
            instrument = position.instrument

            #################
            # Position Size #
            #################
            size_col = 's:{}'.format(instrument.name)
            size_cols.append(size_col)
            size_history = pd.DataFrame(position.sizeHistory, columns=[size_col, 'when'])
            size_history.set_index('when', inplace=True)
            portfolio.append(size_history)

            price_col = instrument.name
            price_history = pd.DataFrame(position.instrumentPriceHistory, columns=[price_col, 'when'])
            price_history.set_index('when', inplace=True)
            portfolio.append(price_history)

        return self._constructDf(portfolio)[size_cols]

    def getSizeAll(self):
        portfolio = []
        size_cols = []
        for position in self.allPositions():
            instrument = position.instrument

            #################
            # Position Size #
            #################
            size_col = 's:{}'.format(instrument.name)
            size_cols.append(size_col)
            size_history = pd.DataFrame(position.sizeHistory, columns=[size_col, 'when'])
            size_history.set_index('when', inplace=True)
            portfolio.append(size_history)

            price_col = instrument.name
            price_history = pd.DataFrame(position.instrumentPriceHistory, columns=[price_col, 'when'])
            price_history.set_index('when', inplace=True)
            portfolio.append(price_history)

        return self._constructDf(portfolio)[size_cols]

    def getNotional(self, strategy):
        portfolio = []
        notional_cols = []
        for position in self.positions(strategy):
            instrument = position.instrument

            #################
            # Position Size #
            #################
            notional_col = 'n:{}'.format(instrument.name)
            notional_cols.append(notional_col)
            notional_history = pd.DataFrame(position.notionalHistory, columns=[notional_col, 'when'])
            notional_history.set_index('when', inplace=True)
            portfolio.append(notional_history)

            price_col = instrument.name
            price_history = pd.DataFrame(position.instrumentPriceHistory, columns=[price_col, 'when'])
            price_history.set_index('when', inplace=True)
            portfolio.append(price_history)

        return self._constructDf(portfolio)[notional_cols]

    def getNotionalAll(self, ):
        portfolio = []
        notional_cols = []
        for position in self.allPositions():
            instrument = position.instrument

            #################
            # Position Size #
            #################
            notional_col = 'n:{}'.format(instrument.name)
            notional_cols.append(notional_col)
            notional_history = pd.DataFrame(position.notionalHistory, columns=[notional_col, 'when'])
            notional_history.set_index('when', inplace=True)
            portfolio.append(notional_history)

            price_col = instrument.name
            price_history = pd.DataFrame(position.instrumentPriceHistory, columns=[price_col, 'when'])
            price_history.set_index('when', inplace=True)
            portfolio.append(price_history)
        return self._constructDf(portfolio)[notional_cols]

    def getInvestment(self, strategy):
        portfolio = []
        investment_cols = []
        for position in self.positions(strategy):
            instrument = position.instrument

            #################
            # Position Size #
            #################
            investment_col = 'i:{}'.format(instrument.name)
            investment_cols.append(investment_col)
            investment_history = pd.DataFrame(position.investmentHistory, columns=[investment_col, 'when'])
            investment_history.set_index('when', inplace=True)
            portfolio.append(investment_history)

            price_col = instrument.name
            price_history = pd.DataFrame(position.instrumentPriceHistory, columns=[price_col, 'when'])
            price_history.set_index('when', inplace=True)
            portfolio.append(price_history)

        return self._constructDf(portfolio)[investment_cols]

    def save(self, filename_prefix):
        with open('{}.prices.json'.format(filename_prefix), 'w') as fp:
            json.dump({json.dumps(k.toJson()): v for k, v in self._prices.items()}, fp, cls=_Serializer)

        with open('{}.trades.json'.format(filename_prefix), 'w') as fp:
            json.dump({json.dumps(k.toJson()): v for k, v in self._trades.items()}, fp, cls=_Serializer)

        with open('{}.active_by_inst.json'.format(filename_prefix), 'w') as fp:
            json.dump({json.dumps(k.toJson()): v for k, v in self._active_positions_by_instrument.items()}, fp, cls=_Serializer)

        with open('{}.active_by_strat.json'.format(filename_prefix), 'w') as fp:
            json.dump({k: {json.dumps(kk.toJson()): vv for kk, vv in v.items()}
                       for k, v in self._active_positions_by_strategy.items()}, fp, cls=_Serializer)

    def restore(self, filename_prefix):
        with open('{}.prices.json'.format(filename_prefix), 'r') as fp:
            jsn = json.load(fp)
            self._prices = {
                Instrument.fromJson(json.loads(k)): [(p1, datetime.fromtimestamp(p2)) for p1, p2 in v] for k, v in jsn.items()
            }

        with open('{}.trades.json'.format(filename_prefix), 'r') as fp:
            jsn = json.load(fp)
            self._trades = {
                Instrument.fromJson(json.loads(k)): [Trade.fromJson(x) for x in v] for k, v in jsn.items()
            }

        with open('{}.active_by_inst.json'.format(filename_prefix), 'r') as fp:
            jsn = json.load(fp)
            self._active_positions_by_instrument = {
                Instrument.fromJson(json.loads(k)): [Position.fromJson(vv) for vv in v] for k, v in jsn.items()
            }

        with open('{}.active_by_strat.json'.format(filename_prefix), 'r') as fp:
            jsn = json.load(fp)
            self._active_positions_by_strategy = {
                k: {
                    Instrument.fromJson(json.loads(kk)): Position.fromJson(vv) for kk, vv in v.items()
                } for k, v in jsn.items()
            }
