import os
from aat.core import ExchangeType, Order
from aat.config import TradingType
from aat.exchange import Exchange
from .accounts import _get_accounts
from .client import CoinbaseExchangeAuth
from .define import _REST, _REST_SANDBOX, _WS, _WS_SANDBOX
from .instruments import _get_instruments
from .orders import _new_order, _cancel_order


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

    # ******************* #
    # Market Data Methods #
    # ******************* #
    async def tick(self):
        '''return data from exchange'''

    async def subscribe(self, instrument):
        self._subscriptions.append(instrument)

    # ******************* #
    # Order Entry Methods #
    # ******************* #
    async def accounts(self):
        '''get accounts from source'''
        return _get_accounts(self._client, self.exchange())

    async def newOrder(self, order):
        '''submit a new order to the exchange. should set the given order's `id` field to exchange-assigned id'''
        _ = _new_order(self._client, order)  # TODO

    async def cancelOrder(self, order: Order):
        '''cancel a previously submitted order to the exchange.'''
        _ = _cancel_order(self._client, order)  # TODO


Exchange.registerExchange('coinbase', CoinbaseProExchange)
