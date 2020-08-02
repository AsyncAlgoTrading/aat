import pyEX
from ..exchange import Exchange
# from ...config import InstrumentType, Side, OrderType
from ...core import ExchangeType


class IEX(Exchange):
    '''Investor's Exchange'''

    def __init__(self):
        super().__init__(ExchangeType('iex'))

    # *************** #
    # General methods #
    # *************** #
    async def connect(self):
        '''connect to exchange. should be asynchronous.

        For OrderEntry-only, can just return None
        '''
        self._client = pyEX.Client()

    # ******************* #
    # Market Data Methods #
    # ******************* #
    async def instruments(self):
        '''get list of available instruments'''
        return []

    async def tick(self):
        '''return data from exchange'''

    # ******************* #
    # Order Entry Methods #
    # ******************* #
    # Not implemented, data-only


Exchange.registerExchange('iex', IEX)
