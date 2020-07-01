from aat.core import Order, Event
from aat.exchange import Exchange


class OrderManager(object):
    def __init__(self):
        # map exchangetype to exchange instance
        self._exchanges = {}

        # track which strategies generated which orders
        self._pending_orders = {}

        # past orders
        self._past_orders = []

    def addExchange(self, exchange: Exchange):
        '''add an exchange'''
        self._exchanges[exchange.exchange()] = exchange

    def _setManager(self, manager):
        '''install manager'''
        self._manager = manager

    # *********************
    # Order Entry Methods *
    # *********************
    async def newOrder(self, strategy, order: Order):
        exchange = self._exchanges.get(order.exchange)
        if not exchange:
            raise Exception('Exchange not installed: {}'.format(order.exchange))

        await exchange.newOrder(order)
        self._pending_orders[order.id] = (order, strategy)
        return order

    # **********************
    # EventHandler methods *
    # **********************
    async def onTrade(self, event):
        '''Match trade with order'''
        action, strat, order = False, None, None

        for order in event.target.maker_orders:
            if order.id in self._pending_orders:
                action = True
                _, strat = self._pending_orders[order.id]
                break

        if event.target.taker_order.id in self._pending_orders:
            action = True
            order = event.target.taker_order
            _, strat = self._pending_orders[order.id]

        if action:
            if order.side == Order.Sides.SELL:
                await self._manager._onSold(strat, event.target, order)
            else:
                await self._manager._onBought(strat, event.target, order)
            del self._pending_orders[order.id]

    async def onCancel(self, event):
        order = event.target
        if order.id in self._pending_orders:
            _, strat = self._pending_orders[order.id]

            await self._manager._onReject(strat, event)
            del self._pending_orders[order.id]

    async def onOpen(self, event: Event):
        # TODO
        pass

    async def onFill(self, event: Event):
        # TODO
        pass

    async def onChange(self, event: Event):
        # TODO
        pass

    async def onHalt(self, data):
        # TODO
        pass

    async def onContinue(self, data):
        # TODO
        pass

    async def onData(self, event):
        # TODO
        pass

    async def onError(self, event):
        # TODO
        pass

    async def onExit(self, event):
        # TODO
        pass

    async def onStart(self, event):
        # TODO
        pass
