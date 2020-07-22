from abc import abstractmethod
from .base.market_data import _MarketData
from .base.order_entry import _OrderEntry


_EXCHANGES = {}


class Exchange(_MarketData, _OrderEntry):
    '''Generic representation of an exchange. There are two primary functionalities of an exchange.

    Market Data Source:
        exchanges can stream data to the engine

    Order Entry Sink:
        exchanges can be queried for data, or send data
    '''

    def __init__(self, exchange: str):
        self._exchange = exchange

    def exchange(self):
        return self._exchange

    @staticmethod
    def registerExchange(exchange_name, clazz):
        _EXCHANGES[exchange_name] = clazz

    @staticmethod
    def exchanges(exchange=None):
        if exchange:
            if exchange not in _EXCHANGES:
                raise Exception(f'Unknown exchange type: {exchange}')
            return _EXCHANGES[exchange]
        return list(_EXCHANGES.keys())

    @abstractmethod
    async def connect(self):
        '''connect to exchange. should be asynchronous.

        For OrderEntry-only, can just return None
        '''
    # ****************** #
    # Inherited  methods #

    # From _MarketData
    #
    # async def tick(self):

    # From _OrderEntry
    #
    # async def newOrder(self, order: Order):
    # def accounts(self) -> List:
    # ************************** #
