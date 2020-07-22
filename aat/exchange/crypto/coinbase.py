from ..exchange import Exchange
from ...core import ExchangeType


class CoinbaseProExchange(Exchange):
    '''Coinbase Pro Exchange'''

    def __init__(self):
        super().__init__(ExchangeType('coinbasepro'))

    # *************** #
    # General methods #
    # *************** #
    async def connect(self):
        '''connect to exchange. should be asynchronous.'''

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
        '''submit a new order to the exchange. should set the given order's `id` field to exchange-assigned id'''


Exchange.registerExchange('coinbase', CoinbaseProExchange)
