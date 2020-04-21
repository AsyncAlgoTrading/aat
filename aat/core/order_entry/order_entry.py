from aat.core import Order
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
        print(order.id)
        self._pending_orders[order.id] = (order, strategy)

    def onTrade(self, event):
        print('-->', list(self._pending_orders.keys()))
        print(list(x.id for x in event.target.maker_orders))
        print(event.target.taker_order.id)
        for order in event.target.maker_orders:
            if order.id in self._pending_orders:
                raise Exception('Here1')
        if event.target.taker_order.id in self._pending_orders:
            raise Exception('Here2')
