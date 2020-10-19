import os
from collections import deque

from aat.core import ExchangeType, Order, Event
from aat.config import TradingType, InstrumentType, EventType
from aat.exchange import Exchange

from .client import CoinbaseExchangeClient


class CoinbaseProExchange(Exchange):
    '''Coinbase Pro Exchange'''

    def __init__(self,
                 trading_type,
                 verbose,
                 api_key='',
                 api_secret='',
                 api_passphrase='',
                 **kwargs):
        self._trading_type = trading_type
        self._verbose = verbose

        self._api_key = api_key or os.environ.get('API_KEY', '')
        self._api_secret = api_key or os.environ.get('API_SECRET', '')
        self._api_passphrase = api_key or os.environ.get('API_PASSPHRASE', '')

        if not (self._api_key and self._api_secret and self._api_passphrase):
            raise Exception('No coinbase auth!')

        if trading_type == TradingType.BACKTEST:
            raise NotImplementedError()

        if self._trading_type == TradingType.SANDBOX:
            super().__init__(ExchangeType('coinbaseprosandbox'))
        else:
            print('*' * 100)
            print('*' * 100)
            print('WARNING: LIVE TRADING')
            print('*' * 100)
            print('*' * 100)
            super().__init__(ExchangeType('coinbasepro'))

        self._client = CoinbaseExchangeClient(self._trading_type, self.exchange(), self._api_key, self._api_secret, self._api_passphrase)

        self._order_events = deque()
        self._data_events = deque()

        # TODO
        self._subscriptions = []

    # *************** #
    # General methods #
    # *************** #
    async def connect(self):
        '''connect to exchange. should be asynchronous.'''
        # instantiate instruments
        self._client.instruments()

    async def lookup(self, instrument):
        '''lookup an instrument on the exchange'''
        # TODO
        raise NotImplementedError()

    # ******************* #
    # Market Data Methods #
    # ******************* #
    async def tick(self):
        '''return data from exchange'''
        for item in self._client.orderBook(self._subscriptions):
            yield item

        async for tick in self._client.websocket(self._subscriptions):
            yield tick

    async def subscribe(self, instrument):
        if instrument.type == InstrumentType.PAIR:
            self._subscriptions.append(instrument)

    # ******************* #
    # Order Entry Methods #
    # ******************* #
    async def accounts(self):
        '''get accounts from source'''
        return self._client.accounts()

    async def newOrder(self, order):
        '''submit a new order to the exchange. should set the given order's `id` field to exchange-assigned id'''
        ret = self._client.newOrder(order)
        if ret:
            # order succesful
            self._order_events.append(Event(type=EventType.RECEIVED, target=order))
        else:
            # order failute
            self._order_events.append(Event(type=EventType.REJECTED, target=order))

    async def cancelOrder(self, order: Order):
        '''cancel a previously submitted order to the exchange.'''
        _ = self._client.cancelOrder(order)


Exchange.registerExchange('coinbase', CoinbaseProExchange)
