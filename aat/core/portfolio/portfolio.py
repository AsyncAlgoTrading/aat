import pandas as pd  # type: ignore
from aat.config import Side
from aat.core import Event, Order, Trade, Instrument, ExchangeType, Position
from aat.core.engine.manager import ManagerBase


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

    def newPosition(self, strategy, trade):
        my_order: Order = trade.my_order

        if trade.instrument in self._active_positions_by_instrument and \
           strategy in self._active_positions_by_strategy:

            # update position
            cur_pos = self._active_positions_by_strategy[strategy][trade.instrument]
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
            if strategy not in self._active_positions_by_strategy:
                self._active_positions_by_strategy[strategy] = {}
            
            # if not tracking instrument yet, add
            if instrument not in self._active_positions_by_instrument:
                self._active_positions_by_instrument = []

            # Map position in by strategy
            self._active_positions_by_strategy[strategy][trade.instrument] = Position(price=trade.price,
                                                                                      size=trade.volume,
                                                                                      timestamp=trade.timestamp,
                                                                                      instrument=trade.instrument,
                                                                                      exchange=trade.exchange,
                                                                                      trades=[trade])

            # map a single position by instrument
            self._active_positions_by_instrument[trade.instrument].append(
                self._active_positions_by_strategy[strategy][trade.instrument]
            )
                            

    def positions(self, instrument: Instrument = None, exchange: ExchangeType = None, side: Side = None):
        # TODO
        return list(sum(x) for x in self._active_positions_by_instrument.values())

    def priceHistory(self, instrument: Instrument = None):
        if instrument:
            return pd.DataFrame(self._prices[instrument], columns=[instrument.name, 'when'])
        return {i: pd.DataFrame(self._prices[i], columns=[i.name, 'when']) for i in self._prices}

    def onTrade(self, trade):
        # TODO move
        if trade.instrument in self._active_positions_by_instrument:

            for pos in self._active_positions_by_instrument[trade.instrument]:
                pos = self._active_positions[trade.instrument]
                pos.unrealizedPnl = (pos.size * (trade.price - pos.price), trade.timestamp)
                pos.pnl = (pos.pnl, trade.timestamp)
                pos.instrumentPrice = (trade.price, trade.timestamp)

        if trade.instrument not in self._prices:
            self._prices[trade.instrument] = [(trade.price, trade.timestamp)]
            self._trades[trade.instrument] = [trade]
        else:
            self._prices[trade.instrument].append((trade.price, trade.timestamp))
            self._trades[trade.instrument].append(trade)

    async def onTraded(self, trade):
        self.newPosition(trade)
