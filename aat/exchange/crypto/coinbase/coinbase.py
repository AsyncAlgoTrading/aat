import aiohttp
import os
import json
from collections import deque

from aat.core import ExchangeType, Order, Event
from aat.config import TradingType, EventType, InstrumentType
from aat.exchange import Exchange

from .accounts import _get_accounts
from .client import CoinbaseExchangeAuth
from .define import _REST, _REST_SANDBOX, _WS, _WS_SANDBOX, _SUBSCRIPTION
from .instruments import _get_instruments
from .orders import _new_order, _cancel_order, _order_book


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

        if trading_type == TradingType.BACKTEST:
            raise NotImplementedError()

        if self._trading_type == TradingType.SANDBOX:
            super().__init__(ExchangeType('coinbaseprosandbox'))
            self._api_url = _REST
            self._ws_url = _WS
        else:
            print('*' * 100)
            print('*' * 100)
            print('WARNING: LIVE TRADING')
            print('*' * 100)
            print('*' * 100)
            super().__init__(ExchangeType('coinbasepro'))
            self._api_url = _REST_SANDBOX
            self._ws_url = _WS_SANDBOX

        self._client = CoinbaseExchangeAuth(self._api_url, self._ws_url, self._api_key, self._api_secret, self._api_passphrase)

        self._order_events = deque()

        # TODO
        self._subscriptions = []

    # *************** #
    # General methods #
    # *************** #
    async def connect(self):
        '''connect to exchange. should be asynchronous.'''
        # instantiate instruments
        _get_instruments(self._client, self.exchange())

    async def lookup(self, instrument):
        '''lookup an instrument on the exchange'''
        # TODO
        raise NotImplementedError()

    def _ob(self):
        for sub in self._subscriptions:
            _order_book(self._client, sub)

    def _ws_subscription(self):
        subscription = _SUBSCRIPTION.copy()
        for sub in self._subscriptions:
            subscription['product_ids'].append(sub.brokerId)
        self._client.subscription(subscription)
        return subscription

    # ******************* #
    # Market Data Methods #
    # ******************* #
    async def tick(self):
        '''return data from exchange'''
        for item in self._ob():
            yield item

        session = aiohttp.ClientSession()
        async with session.ws_connect(self._ws_url) as ws:
            await ws.send_str(json.dumps(self._ws_subscription()))

            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    x = msg.data
                    print(x)

        yield

    async def subscribe(self, instrument):
        if instrument.type == InstrumentType.PAIR:
            self._subscriptions.append(instrument)

    # ******************* #
    # Order Entry Methods #
    # ******************* #
    async def accounts(self):
        '''get accounts from source'''
        return _get_accounts(self._client, self.exchange())

    async def newOrder(self, order):
        '''submit a new order to the exchange. should set the given order's `id` field to exchange-assigned id'''
        ret = _new_order(self._client, order)  # TODO
        if ret:
            # order succesful
            self._order_events.append(Event(type=EventType.RECEIVED, target=order))
        else:
            # order failute
            self._order_events.append(Event(type=EventType.REJECTED, target=order))

    async def cancelOrder(self, order: Order):
        '''cancel a previously submitted order to the exchange.'''
        _ = _cancel_order(self._client, order)  # TODO


Exchange.registerExchange('coinbase', CoinbaseProExchange)
