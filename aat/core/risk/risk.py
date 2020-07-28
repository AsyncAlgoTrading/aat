from aat.config import Side
from aat.core import Event, Order, Trade, Instrument, ExchangeType, Position


class RiskManager(object):
    def __init__(self):
        self._active_orders = []
        self._active_positions = {}
        self._instrument_positions_map = {}

    def _setManager(self, manager):
        '''install manager'''
        self._manager = manager

    def newPosition(self, trade: Trade):
        if trade.id in self._active_positions:
            # update position
            cur_pos = self._active_positions[trade.id]
            cur_pos.trades.append(trade)

            # TODO update notional/size/price etc
            prev_size = cur_pos.size
            prev_notional = cur_pos.notional
            prev_price = cur_pos.price

            cur_pos.size += trade.volume if trade.side == Side.BUY else -1 * trade.volume

            if (prev_size > 0 and cur_pos.size > prev_size) or (prev_size < 0 and cur_pos.size < prev_size):
                # increasing position size
                # update average price
                cur_pos.price = (prev_notional + (trade.volume * trade.price)) / cur_pos.size

            elif (prev_size > 0 and cur_pos.size < 0) or (prev_size < 0 and cur_pos.size > 0):
                # decreasing position size in one direction, increasing position size in other

                # update realized pnl
                cur_pos.pnl += (prev_size * (trade.price - prev_price))  # update realized pnl with closing position

                # update average price
                cur_pos.price = trade.price

            else:
                # decreasing position size
                # update realized pnl
                cur_pos.pnl += (trade.volume * (prev_price - trade.price))  # update realized pnl with closing position

            # TODO close if side is 0

        else:
            self._active_positions[trade.id] = Position(price=trade.price,
                                                        size=trade.volume,
                                                        notional=trade.volume * trade.price,
                                                        instrument=trade.instrument,
                                                        exchange=trade.exchange,
                                                        trades=[trade])

            self._instrument_positions_map[trade.instrument] = self._active_positions[trade.id]

    # *********************
    # Risk Methods        *
    # *********************
    def positions(self, instrument: Instrument = None, exchange: ExchangeType = None, side: Side = None):
        return list(self._active_positions.values())

    def risk(self, position=None):
        return "risk"

    # *********************
    # Order Entry Methods *
    # *********************
    async def newOrder(self, strategy, order: Order):
        # TODO
        self._active_orders.append(order)  # TODO use strategy
        return order, True

    # **********************
    # EventHandler methods *
    # **********************
    async def onTrade(self, event: Event):
        trade: Trade = event.target  # type: ignore
        # TODO
        if trade.instrument in self._instrument_positions_map:
            pos = self._instrument_positions_map[trade.instrument]
            pos.unrealizedPnl = pos.size * (trade.price - pos.price)

    async def onCancel(self, event):
        # TODO
        pass

    async def onOpen(self, event: Event):
        # TODO
        pass

    async def onFill(self, event: Event):
        # TODO
        pass

    async def onChange(self, event: Event):
        # TODO
        pass

    async def onData(self, event: Event):
        # TODO
        pass

    async def onHalt(self, event: Event):
        # TODO
        pass

    async def onContinue(self, event: Event):
        # TODO
        pass

    async def onError(self, event: Event):
        # TODO
        pass

    async def onStart(self, event: Event):
        # TODO
        pass

    async def onExit(self, event: Event):
        # TODO
        pass

    #########################
    # Order Entry Callbacks #
    #########################
    async def onBought(self, event: Event):
        trade: Trade = event.target  # type: ignore
        self._active_orders.remove(trade.my_order)
        self.newPosition(trade)

    async def onSold(self, event: Event):
        trade: Trade = event.target  # type: ignore
        self._active_orders.remove(trade.my_order)
        self.newPosition(trade)

    async def onRejected(self, event: Event):
        order: Order = event.target  # type: ignore
        self._active_orders.remove(order)
