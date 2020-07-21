from random import randint
from ibapi.client import EClient  # type: ignore
from ibapi.wrapper import EWrapper  # type: ignore
from ..exchange import Exchange
from ...core import ExchangeType


class _API(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)


class InteractiveBrokersExchange(Exchange):
    '''Interactive Brokers Exchange'''

    def __init__(self):
        super().__init__(ExchangeType('interactivebrokers'))
        self._api = _API()

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


Exchange.registerExchange('ib', InteractiveBrokersExchange)
