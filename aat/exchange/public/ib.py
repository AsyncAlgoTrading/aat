import asyncio
import threading
from queue import Queue
from random import randint

from ibapi.client import EClient  # type: ignore
from ibapi.wrapper import EWrapper  # type: ignore
from ibapi.contract import Contract, ComboLeg  # type: ignore
from ibapi.order import Order  # type: ignore

from aat.exchange import Exchange
from aat.config import EventType, InstrumentType, OrderType, TradingType
from aat.core import ExchangeType, Event, Trade


def _constructContractAndOrder(aat_order):
    '''Construct an IB contract and order from an Order object'''
    contract = Contract()

    instrument = aat_order.instrument

    if instrument.type == InstrumentType.EQUITY:
        contract.symbol = instrument.name
        contract.secType = "STK"
        contract.currency = instrument.currency.name or "USD"
        contract.exchange = instrument.brokerExchange or "SMART"

    elif instrument.type == InstrumentType.BOND:
        # enter CUSIP as symbol
        contract.symbol = instrument.name  # cusip e.g. 912828C57
        contract.secType = "BOND"
        contract.exchange = instrument.brokerExchange or "SMART"
        contract.currency = instrument.currency.name or "USD"

    elif instrument.type == InstrumentType.OPTION:
        # contract.symbol = "GOOG"
        contract.secType = "OPT"
        contract.exchange = instrument.brokerExchange or "SMART"
        contract.currency = instrument.currency.name or "USD"
        # contract.lastTradeDateOrContractMonth = "20170120"
        # contract.strike = 615
        # contract.right = "C"
        # contract.multiplier = "100"
        contract.localSymbol = instrument.name  # e.g. "P BMW  JUL 20  4650"
        #                                        can swap name for the above
        #                                        commented out stuff

    elif instrument.type == InstrumentType.FUTURE:
        # contract.symbol = "ES";
        contract.secType = "FUT"
        contract.exchange = instrument.brokerExchange or "SMART"
        contract.currency = instrument.currency.name or "USD"
        # contract.lastTradeDateOrContractMonth = "201803";
        # contract.Multiplier = "5";

        contract.localSymbol = instrument.name  # e.g. "ESU6"
        #                                        swap for commented

    elif instrument.type == InstrumentType.PAIR:
        contract.symbol = instrument.leg1  # "EUR"
        contract.secType = "CASH"
        contract.currency = instrument.leg2  # "GBP"
        contract.exchange = instrument.brokerExchange or "IDEALPRO"

    elif instrument.type == InstrumentType.FUTURESOPTION:
        contract.symbol = "ES"
        contract.secType = "FOP"
        contract.exchange = instrument.brokerExchange
        contract.currency = instrument.currency.name or "USD"
        contract.lastTradeDateOrContractMonth = "20180316"
        contract.strike = 2800
        contract.right = "C"
        contract.multiplier = "50"

    elif instrument.type == InstrumentType.MUTUALFUND:
        contract.symbol = instrument.name  # "VINIX"
        contract.secType = "FUND"
        contract.exchange = instrument.brokerExchange or "FUNDSERV"
        contract.currency = instrument.currency.name or "USD"

    elif instrument.type == InstrumentType.COMMODITIES:
        contract.symbol = instrument.name  # "XAUUSD"
        contract.secType = "CMDTY"
        contract.exchange = instrument.brokerExchange or "SMART"
        contract.currency = instrument.currency.name or "USD"

    elif instrument.type == InstrumentType.SPREAD:
        contract.symbol = instrument.name
        contract.secType = "BAG"
        contract.currency = instrument.currency.name or "USD"
        contract.exchange = instrument.brokerExchange or "SMART"

        leg1 = ComboLeg()
        leg1.conId = 43645865  # IBKR STK  # TODO
        leg1.ratio = 1  # TODO
        leg1.action = instrument.leg1_side
        leg1.exchange = instrument.brokerExchange or "SMART"

        leg2 = ComboLeg()
        leg2.conId = 9408  # MCD STK  # TODO
        leg2.ratio = 1  # TODO
        leg2.action = instrument.leg2_side
        leg2.exchange = instrument.brokerExchange or "SMART"

        contract.comboLegs = [leg1, leg2]

    elif instrument.type == InstrumentType.CURRENCY:
        raise NotImplementedError()

    elif instrument.type == InstrumentType.INDEX:
        raise NotImplementedError()

    else:
        raise NotImplementedError()

    order = Order()
    order.action = aat_order.side.value

    if aat_order.order_type == OrderType.MARKET:
        order.orderType = "MKT"
        order.totalQuantity = aat_order.volume

    elif aat_order.order_type == OrderType.LIMIT:
        order.orderType = "LMT"
        order.totalQuantity = aat_order.volume
        order.lmtPrice = aat_order.price

    elif aat_order.order_type == OrderType.STOP:
        if aat_order.stop_target.order_type == OrderType.MARKET:
            order.orderType = "STP"
            order.auxPrice = aat_order.price
            order.totalQuantity = aat_order.stop_target.volume

        elif aat_order.stop_target.order_type == OrderType.LIMIT:
            order.orderType = "STP LMT"
            order.totalQuantity = aat_order.stop_target.volume
            order.lmtPrice = aat_order.stop_target.price
            order.auxPrice = aat_order.price

        else:
            raise NotImplementedError()

    else:
        raise NotImplementedError()

    return contract, order


class _API(EWrapper, EClient):
    def __init__(self, order_event_queue, market_data_queue):
        EClient.__init__(self, self)
        self.nextOrderId = None
        self._order_event_queue = order_event_queue
        self._market_data_queue = market_data_queue

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextOrderId = orderId

    def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
        self._order_event_queue.put(dict(orderId=orderId,
                                         status=status,
                                         filled=filled,
                                         remaining=remaining,
                                         avgFullPrice=avgFullPrice,
                                         permId=permId,
                                         parentId=parentId,
                                         lastFillPrice=lastFillPrice,
                                         clientId=clientId,
                                         whyHeld=whyHeld,
                                         mktCapPrice=mktCapPrice))


class InteractiveBrokersExchange(Exchange):
    '''Interactive Brokers Exchange'''

    def __init__(self, trading_type=None, verbose=False, **kwargs):
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
        self._api = _API(self._order_event_queue, self._market_data_queue)

    # *************** #
    # General methods #
    # *************** #
    async def instruments(self):
        '''get list of available instruments'''
        # TODO
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
                    t = Trade(maker_orders=[], taker_order=order)
                    t.my_order = order
                    e = Event(type=EventType.TRADE, target=t)
                    yield e
            await asyncio.sleep(0)

        # clear market data events
        # TODO

    # ******************* #
    # Order Entry Methods #
    # ******************* #
    def accounts(self):
        '''get accounts from source'''
        # TODO
        return []

    async def newOrder(self, order):
        '''submit a new order to the exchange. should set the given order's `id` field to exchange-assigned id

        For MarketData-only, can just return None
        '''

        # construct IB contract and order
        ibcontract, iborder = _constructContractAndOrder(order)

        # get id
        id = self._api.nextOrderId

        # send to IB
        self._api.placeOrder(id, ibcontract, iborder)

        # update order id
        order.id = id
        self._orders[order.id] = order

        # increment for next order
        self._api.nextOrderId += 1

    async def cancelOrder(self, order: Order):
        '''cancel a previously submitted order to the exchange.

        For MarketData-only, can just return None
        '''
        self._api.cancelOrder(order.id)


Exchange.registerExchange('ib', InteractiveBrokersExchange)
