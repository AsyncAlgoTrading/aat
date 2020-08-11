import asyncio
import threading
from queue import Queue
from random import randint

from ibapi.client import EClient  # type: ignore
from ibapi.wrapper import EWrapper  # type: ignore
from ibapi.order import Order  # type: ignore

from aat.exchange import Exchange
from aat.config import EventType, TradingType
from aat.core import ExchangeType, Event, Trade

from .utils import _constructContract, _constructContractAndOrder, _constructInstrument


class _API(EWrapper, EClient):
    def __init__(self, order_event_queue, market_data_queue, contract_info_queue):
        EClient.__init__(self, self)
        self.nextOrderId = None
        self.nextReqId = 1

        self._order_event_queue = order_event_queue
        self._market_data_queue = market_data_queue
        self._contract_info_queue = contract_info_queue

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextOrderId = orderId

    def reqContractDetails(self, contract):
        super().reqContractDetails(self.nextReqId, contract)
        self.nextReqId += 1

    def placeOrder(self, contract, order):
        super().placeOrder(self.nextOrderId, contract, order)
        self.nextOrderId += 1
        return self.nextOrderId - 1

    def contractDetails(self, reqId, contractDetails):
        self._contract_info_queue.put(contractDetails)

    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
        self._order_event_queue.put(dict(orderId=orderId,
                                         status=status,
                                         filled=filled,
                                         remaining=remaining,
                                         avgFillPrice=avgFillPrice,
                                         permId=permId,
                                         parentId=parentId,
                                         lastFillPrice=lastFillPrice,
                                         clientId=clientId,
                                         whyHeld=whyHeld,
                                         mktCapPrice=mktCapPrice))


class InteractiveBrokersExchange(Exchange):
    '''Interactive Brokers Exchange'''

    def __init__(self, trading_type, verbose, **kwargs):
        self._trading_type = trading_type
        self._verbose = verbose

        if self._trading_type == TradingType.LIVE:
            super().__init__(ExchangeType('interactivebrokers'))
        else:
            super().__init__(ExchangeType('interactivebrokerspaper'))

        # map order.id to order
        self._orders = {}

        # IB TWS gateway
        self._order_event_queue = Queue()
        self._market_data_queue = Queue()
        self._contract_lookup_queue = Queue()
        self._api = _API(self._order_event_queue, self._market_data_queue, self._contract_lookup_queue)

    # *************** #
    # General methods #
    # *************** #
    async def instruments(self):
        '''get list of available instruments'''
        return []

    async def connect(self):
        '''connect to exchange. should be asynchronous.

        For OrderEntry-only, can just return None
        '''
        if self._trading_type == TradingType.LIVE:
            self._api.connect('127.0.0.1', 7496, randint(0, 10000))
            raise NotImplementedError()

        else:
            self._api.connect('127.0.0.1', 7497, randint(0, 10000))
            self._api_thread = threading.Thread(target=self._api.run, daemon=True)
            self._api_thread.start()

        while self._api.nextOrderId is None:
            print('waiting for IB connect...')
            await asyncio.sleep(1)

        print('IB connected!')

    async def lookup(self, instrument):
        self._api.reqContractDetails(_constructContract(instrument))
        i = 0
        while i < 5:
            if self._contract_lookup_queue.qsize() > 0:
                ret = []
                while self._contract_lookup_queue.qsize() > 0:
                    contract_details = self._contract_lookup_queue.get()
                    ret.append(_constructInstrument(contract_details.contract))
                return ret
            else:
                await asyncio.sleep(1)
                i += 1

    # ******************* #
    # Market Data Methods #
    # ******************* #

    async def tick(self):
        '''return data from exchange'''
        while True:
            # clear order events
            while self._order_event_queue.qsize() > 0:
                order_data = self._order_event_queue.get()
                status = order_data['status']
                order = self._orders[order_data['orderId']]

                if status in ('ApiPending', 'PendingSubmit', 'PendingCancel', 'PreSubmitted', 'ApiCancelled', 'Inactive'):
                    # ignore
                    continue

                elif status in ('Submitted',):
                    # TODO more granular order events api?
                    # ignore
                    pass

                elif status in ('Cancelled',):
                    e = Event(type=EventType.REJECTED, target=order)
                    yield e

                elif status in ('Filled',):
                    t = Trade(volume=order_data['filled'], price=order_data['avgFillPrice'], maker_orders=[], taker_order=order)
                    t.my_order = order
                    e = Event(type=EventType.TRADE, target=t)
                    yield e
            await asyncio.sleep(0)

        # clear market data events
        # TODO

    # ******************* #
    # Order Entry Methods #
    # ******************* #
    async def accounts(self):
        '''get accounts from source'''
        return []

    async def newOrder(self, order):
        '''submit a new order to the exchange. should set the given order's `id` field to exchange-assigned id

        For MarketData-only, can just return None
        '''

        # construct IB contract and order
        ibcontract, iborder = _constructContractAndOrder(order)

        # send to IB
        id = self._api.placeOrder(ibcontract, iborder)

        # update order id
        order.id = id
        self._orders[order.id] = order

    async def cancelOrder(self, order: Order):
        '''cancel a previously submitted order to the exchange.

        For MarketData-only, can just return None
        '''
        self._api.cancelOrder(order.id)


Exchange.registerExchange('ib', InteractiveBrokersExchange)
