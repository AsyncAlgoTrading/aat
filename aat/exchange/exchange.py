from abc import abstractmethod
from .market_data import _MarketData
from .order_entry import _OrderEntry


_EXCHANGES = {}


class Exchange(_MarketData, _OrderEntry):
    '''Generic representation of an exchange. There are two primary functionalities of an exchange.

    Market Data Source:
        exchanges can stream data to the engine

    Order Entry Sink:
        exchanges can be queried for data, or send data
    '''

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
