from cbpro import PublicClient, AuthenticatedClient, WebsocketClient  # type: ignore

from aat.core import ExchangeType, Order
from aat.config import TradingType, OrderType, OrderFlag, InstrumentType
from aat.exchange import Exchange
from .instruments import _get_instruments
from .define import _REST, _REST_SANDBOX, _WS, _WS_SANDBOX


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

        if trading_type == TradingType.BACKTEST:
            raise NotImplementedError()

        if self._trading_type == TradingType.SANDBOX:
            super().__init__(ExchangeType('coinbaseprosandbox'))
            self._api_url = _REST
            self._ws_url = _WS
        else:
            super().__init__(ExchangeType('coinbasepro'))
            self._api_url = _REST_SANDBOX
            self._ws_url = _WS_SANDBOX

        auth = api_key and api_secret and api_passphrase
        self._public_client = PublicClient()

        self._auth_client = AuthenticatedClient(api_key, api_secret, api_passphrase, api_url=self._api_url) if auth else None

        # TODO
        self._subscriptions = []

        # wait until start to instantiate
        self._ws_client = WebsocketClient(url=self._ws_url, products="BTC-USD")

    # *************** #
    # General methods #
    # *************** #
    async def connect(self):
        '''connect to exchange. should be asynchronous.'''

        # instantiate instruments
        _get_instruments(self._public_client, self.exchange())

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
        # TODO
        raise NotImplementedError()

    async def newOrder(self, order):
        '''submit a new order to the exchange. should set the given order's `id` field to exchange-assigned id'''
        if not self._auth_client:
            raise NotImplementedError()

        if order.instrument.type != InstrumentType.PAIR:
            raise NotImplementedError()

        if order.type == OrderType.LIMIT:
            time_in_force = 'GTC'
            if order.flag == OrderFlag.FILL_OR_KILL:
                time_in_force = 'FOK'
            elif order.flag == OrderFlag.IMMEDIATE_OR_CANCEL:
                time_in_force = 'IOC'

            ret = self._auth_client.place_limit_order(product_id='{}-{}'.format(order.instrument.leg1.name, order.instrument.leg2.name),
                                                      side=order.side.value.lower(),
                                                      price=order.price,
                                                      size=order.volume,
                                                      time_in_force=time_in_force)

        elif order.type == OrderType.MARKET:
            ret = self._auth_client.place_limit_order(product_id='{}-{}'.format(order.instrument.leg1.name, order.instrument.leg2.name),
                                                      side=order.side.value.lower(),
                                                      funds=order.price * order.volume)

        elif order.type == OrderType.STOP:
            # TODO
            raise NotImplementedError()
            # self._auth_client.place_stop_order(product_id='BTC-USD',
            #                             side='buy',
            #                             price='200.00',
            #                             size='0.01')

        # Set ID
        order.id = ret['id']
        return order

    async def cancelOrder(self, order: Order):
        '''cancel a previously submitted order to the exchange.'''
        self._auth_client.cancel_order(order.id)
        return order


Exchange.registerExchange('coinbase', CoinbaseProExchange)
