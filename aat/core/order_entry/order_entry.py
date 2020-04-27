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

    def newOrder(self, order: Order, strategy):
        exchange = self._exchanges.get(order.exchange)
        if not exchange:
            raise Exception('Exchange not installed: {}'.format(order.exchange))

        exchange.newOrder(order)
        self._pending_orders[order.id] = (order, strategy)

    def onTrade(self, event):
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
            # TODO add to event loop
            event = Event(type=Event.Types.TRADE, target=order)
            if order.side == Order.Sides.SELL:
                strat.onSold(event)
            else:
                strat.onBought(event)
            del self._pending_orders[order.id]

    def onCancel(self, event):
        order = event.target
        if order.id in self._pending_orders:
            _, strat = self._pending_orders[order.id]

            # TODO add to event loop
            strat.onReject(event)
            del self._pending_orders[order.id]
