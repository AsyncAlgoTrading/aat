from random import randint
from ibapi.client import EClient  # type: ignore
from ibapi.wrapper import EWrapper  # type: ignore
from ibapi.contract import Contract  # type: ignore
from ibapi.order import Order  # type: ignore
from queue import Queue
from ..exchange import Exchange
# from ...config import InstrumentType, Side, OrderType
from ...core import ExchangeType


def _constructContractAndOrder(order):
    '''Construct an IB contract and order from an Order object'''
    contract = Contract()
    order = Order()

    return contract, order


class _API(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.nextOrderId = None

        def nextValidId(self, orderId: int):
            super().nextValidId(orderId)
            self.nextorderId = orderId

        def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
            print('orderStatus - orderid:', orderId, 'status:', status, 'filled', filled, 'remaining', remaining, 'lastFillPrice', lastFillPrice)

        def openOrder(self, orderId, contract, order, orderState):
            print('openOrder id:', orderId, contract.symbol, contract.secType, '@', contract.exchange, ':', order.action, order.orderType, order.totalQuantity, orderState.status)

        def execDetails(self, reqId, contract, execution):
            print('Order Executed: ', reqId, contract.symbol, contract.secType, contract.currency, execution.execId, execution.orderId, execution.shares, execution.lastLiquidity)


class InteractiveBrokersExchange(Exchange):
    '''Interactive Brokers Exchange'''

    def __init__(self):
        super().__init__(ExchangeType('interactivebrokers'))
        self._api = _API()

        self._order_event_queue = Queue()
        self._market_data_queue = Queue()

    # *************** #
    # General methods #
    # *************** #
    async def connect(self):
        '''connect to exchange. should be asynchronous.

        For OrderEntry-only, can just return None
        '''
        self._api.connect('127.0.0.1', 7497, randint(0, 10000))

    # ******************* #
    # Market Data Methods #
    # ******************* #
    async def tick(self):
        '''return data from exchange'''

    # ******************* #
    # Order Entry Methods #
    # ******************* #
    def accounts(self):
        '''get accounts from source'''
        return []

    async def newOrder(self, order):
        '''submit a new order to the exchange. should set the given order's `id` field to exchange-assigned id

        For MarketData-only, can just return None
        '''
        contract, order = _constructContractAndOrder(order)
        id = self._api.nextOrderId
        self._api.nextOrderId += 1

        self._api.placeOrder(id, contract, order)

    async def cancelOrder(self, order: Order):
        '''cancel a previously submitted order to the exchange.

        For MarketData-only, can just return None
        '''
        self._api.cancelOrder(order.id)


Exchange.registerExchange('ib', InteractiveBrokersExchange)
