import operator
# from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import reduce
from typing import List, Dict
from .enums import TradeResult, ExchangeType, PairType, CurrencyType, TradingType, Side
from .exceptions import QueryException, AATException
from .execution import Execution
from .logging import log
from .risk import Risk
from .strategy import TradingStrategy
from .structs import Instrument, MarketData, TradeRequest, TradeResponse
from .utils import iterate_accounts, pnl_helper, findpath


class QueryEngine(object):
    def __init__(self,
                 trading_type: TradingType = None,
                 exchanges: List[ExchangeType] = None,
                 pairs: List[PairType] = None,
                 instruments: List[Instrument] = None,
                 accounts=None,
                 risk: Risk = None,
                 execution: Execution = None):
        # self._executor = ThreadPoolExecutor(16)
        self._all = []
        self._trading_type = trading_type

        self._accounts = accounts

        # public
        self.positions_value = [[datetime.now(), 0.0, 0.0, 0.0]]
        self.portfolio_value = [[datetime.now(), risk.total_funds]]
        self.positions = {}
        self.pending = {}

        self._trades = []
        self._trades_by_instrument = {}

        self._pairs = pairs

        # public
        self.instruments = instruments
        self.exchanges = exchanges

        self._last_price_by_asset_and_exchange = {}

        self._trade_reqs = []
        self._trade_resps = []
        self._trade_reqs_by_instrument = {}
        self._trade_resps_by_instrument = {}

        # public
        self.strategies = []

        self._risk = risk
        self._execution = execution

    def registerStrategy(self, strat: TradingStrategy):
        self.strategies.append(strat)

    def query_instruments(self, exchange=None) -> List[PairType]:
        '''get list of all instruments available on all exchanges'''
        return self._instruments[exchange] if exchange else reduce(operator.concat, self._instruments.values())

    def query_exchanges(self) -> List[Dict]:
        '''get list of exchanges and their available instruments'''
        return [{'exchange': name, 'instruments': self.query_instruments(name)} for name, ex in self._exchanges.items()]

    def _paginate(self, instrument: Instrument, lst: list, lst_sub: list, page: int = 1) -> list:
        '''paginate a data request'''
        page, from_, to_ = (page, -1 * page * 100, -1 * (page - 1) * 100) if page is not None else (0, 0, -1)

        if instrument:
            return lst_sub[instrument][from_:to_] if page > 1 else lst_sub[instrument][from_:]
        return lst[from_:to_] if page > 1 else lst[from_:]

    def query_lastpriceall(self) -> List[MarketData]:
        '''get last price of all assets'''
        return [m for exs in self._last_price_by_asset_and_exchange.values() for m in exs.values()]

    def query_lastprice(self, instrument: Instrument, exchange: ExchangeType = None) -> MarketData:
        '''get last price of asset, potentially on a given exchange'''
        if instrument not in self._last_price_by_asset_and_exchange:
            raise QueryException('Not found!')
        if exchange:
            if exchange not in self._last_price_by_asset_and_exchange[instrument]:
                raise QueryException('Not found!')
            return self._last_price_by_asset_and_exchange[instrument][exchange]
        if "ANY" not in self._last_price_by_asset_and_exchange[instrument]:
            raise QueryException('Not found!')
        return self._last_price_by_asset_and_exchange[instrument]["ANY"]

    def query_trades(self, instrument: Instrument = None, page: int = 1) -> List[MarketData]:
        '''get trades for instrument'''
        return self._paginate(instrument,
                              self._trades,
                              self._trades_by_instrument,
                              page)

    def query_tradereqs(self, instrument: Instrument = None, page: int = 1) -> List[TradeRequest]:
        '''get trade requests for an instrument'''
        return self._paginate(instrument, self._trade_reqs, self._trade_reqs_by_instrument, page)

    def query_traderesps(self, instrument: Instrument = None, page: int = 1) -> List[TradeResponse]:
        '''get trade responses for an instrument'''
        return self._paginate(instrument, self._trade_resps, self._trade_resps_by_instrument, page)

    def newPending(self, resp: TradeResponse) -> None:
        self.pending[resp.order_id] = resp

    def push_tradereq(self, req: TradeRequest) -> None:
        '''append trade request to list'''
        self._trade_reqs.append(req)
        if req.instrument not in self._trade_reqs_by_instrument:
            self._trade_reqs_by_instrument[req.instrument] = []
        self._trade_reqs_by_instrument[req.instrument].append(req)

    def push_traderesp(self, resp: TradeResponse) -> None:
        '''append trade response to list'''
        if resp.status in (TradeResult.REJECTED, TradeResult.PENDING, TradeResult.NONE):
            return
        self._trade_resps.append(resp)
        if resp.instrument not in self._trade_resps_by_instrument:
            self._trade_resps_by_instrument[resp.instrument] = []
        self._trade_resps_by_instrument[resp.instrument].append(resp)

    def onTrade(self, data: MarketData) -> None:
        '''process market data on trade'''

        # append to list of all data so far
        self._all.append(data)

        # append to list of all trades so far
        self._trades.append(data)

        # if not tracking, initialize list of trades
        if data.instrument not in self._trades_by_instrument:
            self._trades_by_instrument[data.instrument] = []
        # add data to list
        self._trades_by_instrument[data.instrument].append(data)

        # if not tracking by exchange
        if data.instrument not in self._last_price_by_asset_and_exchange:
            self._last_price_by_asset_and_exchange[data.instrument] = {}
        # add data to
        self._last_price_by_asset_and_exchange[data.instrument][data.exchange] = data

        # set data to be last on ANY exchange
        self._last_price_by_asset_and_exchange[data.instrument]['ANY'] = data

        # if any pending orders for this trade
        if data.order_id in self.pending.keys():
            # grab previous pending response
            resp = self.pending[data.order_id]

            # if they're equal, ignore remaining
            resp.volume = resp.remaining - data.remaining if resp != data else resp.volume
            resp.remaining = data.remaining

            # call on fill to strat
            if resp.strategy:
                resp.strategy.onFill(resp)
            else:
                raise Exception('Response has no corresponding strategy!')

            # update account holdings
            self.updateAccounts(resp)

            # update porfolio risk
            self._risk.update(resp)

            # delete pending order if filled
            if data.remaining <= 0:
                del self.pending[data.order_id]
        else:
            # price only
            if data.instrument in self.positions:
                self.positions[data.instrument].price(data.price)

        # recalculate value of positions
        self._recalculate_positions(data)

        # recalculate value of portfolio
        self._recalculate_portfolio(data)

    def onFill(self, resp: TradeResponse) -> None:
        if self._trading_type not in (TradingType.BACKTEST, TradingType.SIMULATION):
            # only used during offline trading
            raise QueryException('Must derive fills from market data!')

        # ignore different responses
        if resp.volume <= 0 or resp.status != TradeResult.FILLED:
            # skip
            return
        resp.remaining = 0.0
        self.onTrade(resp)

    def onCancel(self, data: MarketData) -> None:
        # if pending order
        if data.order_id in self.pending.keys():
            # grab response
            resp = self.pending[data.order_id]

            # delete from tracking
            del self.pending[data.order_id]

            # tell risk
            self._risk.cancel(resp)

    def updateAccounts(self, resp: TradeResponse = None) -> None:
        '''update the holdings and spot value of accounts'''

        # if reacting to a trade response
        if resp:

            # get left and right legs
            account_left = self._accounts[resp.instrument.underlying.value[0]][resp.exchange]
            account_right = self._accounts[resp.instrument.underlying.value[1]][resp.exchange]

            if resp.side == Side.BUY:
                # if buy
                # 5 BTCUSD @ $2 -> from_btc += volume, to_usd -= price*volume
                account_left.balance += resp.volume
                account_right.balance -= resp.volume * resp.price
            else:
                # if sell
                # 5 BTCUSD @ $2 -> from_btc -= volume, to_usd += price*volume
                account_left.balance -= resp.volume
                account_right.balance += resp.volume * resp.price
            # iterate through these
            accounts = (account_left, account_right)
        else:
            # WARNING
            # don't update value on every tick
            log.warn('Iterating through ALL accounts')
            accounts = iterate_accounts(self.accounts)

        # update account values
        for account in accounts:
            log.info(f'Updating value of account {account}')
            if account.currency == CurrencyType.USD:
                # if holding USD, add value
                account.value = account.balance
            else:
                # calculate USD value
                price = self._last_price_by_asset_and_exchange[resp.instrument][resp.exchange].price
                account.value = account.balance * price
            log.info(f'New value: {account}')

    def update_positions(self, resp: TradeResponse) -> None:
        '''update positions based on a trade'''
        if resp.status in (TradeResult.REJECTED, TradeResult.PENDING, TradeResult.NONE):
            '''ignore these as they don't affect what we hold'''
            return

        if resp.instrument not in self.positions:
            self.positions[resp.instrument] = pnl_helper()

        self.positions[resp.instrument].exec(resp.volume, resp.price, resp.side)

    def _recalculate_positions(self, data: MarketData) -> None:
        '''recalculate the market value of active positions'''
        # ignore if not an active position
        if data.instrument not in self.positions:
            return

        volume = self.positions[data.instrument]._volume
        # instrument = str(data.instrument)
        _ = str(data.instrument)
        # value = self.positions[data.instrument]._avg_price * volume
        _ = self.positions[data.instrument]._avg_price * volume
        pnl = self.positions[data.instrument]._pnl

        # get PnL numbers
        unrealized = sum(x._pnl for x in self.positions.values())
        realized = sum(x._realized for x in self.positions.values())
        pnl = sum(x._pnl + x._realized for x in self.positions.values())
        self.portfolio_value.append([data.time, self.portfolio_value[-1][1], unrealized, realized, pnl])

    def _recalculate_portfolio(self, data: MarketData) -> None:
        '''recalculate the market value of all accounts'''
        if data.instrument.underlying.value[0] == CurrencyType.USD:
            left_ret = 1
        else:
            left_ret = self._ticker(data.instrument.underlying.value[0], exchange=self.exchanges[data.exchange])

        if data.instrument.underlying.value[1] == CurrencyType.USD:
            right_ret = 1
        else:
            right_ret = self._ticker(data.instrument.underlying.value[1], exchange=self.exchanges[data.exchange])

        print(left_ret, right_ret)
        self.portfolio_value.append([data.time, self.portfolio_value[-1][-1]])

    def _ticker(self, currency: CurrencyType, exchange):
        inst = Instrument(underlying=PairType.from_string(currency.value + '/USD'))

        if inst in exchange.markets():
            return self.query_lastprice(inst)
        else:
            for stable in ('USD', 'USDC', 'USDT'):
                try:
                    inst = Instrument(underlying=PairType.from_string(currency.value + '/' + stable))
                    inst1, inst2, i1_inverted, i2_inverted = findpath(inst, exchange.markets())
                    broken = False
                except (AATException, ValueError):
                    broken = True
            if broken:
                return None

            inst1_t = self.query_lastprice(instrument=inst1).price
            inst2_t = self.query_lastprice(instrument=inst2).price
            if i1_inverted:
                inst1_t = 1.0 / inst1_t
            if i2_inverted:
                inst2_t = 1.0 / inst2_t
            px = inst1_t * inst2_t
            return px
