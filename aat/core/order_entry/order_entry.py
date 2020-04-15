from aat.core import Order
from aat.exchange import Exchange


class OrderManager(object):
    def __init__(self):
        self._exchanges = {}
        self._pending_orders = {}

    def addExchange(self, exchange: Exchange):
        self._exchanges[exchange.exchange()] = exchange

    def newOrder(self, order: Order):
        exchange = self._exchanges.get(order.exchange)
        if not exchange:
            raise Exception('Exchange not installed: {}'.format(order.exchange))
        exchange.newOrder(order)
