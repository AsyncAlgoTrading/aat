from abc import abstractmethod
from typing import Dict, List, Type, Union

from aat.core import ExchangeType, Instrument

from .base.market_data import _MarketData
from .base.order_entry import _OrderEntry


_EXCHANGES: Dict[str, Type] = {}


class Exchange(_MarketData, _OrderEntry):
    """Generic representation of an exchange. There are two primary functionalities of an exchange.

    Market Data Source:
        exchanges can stream data to the engine

    Order Entry Sink:
        exchanges can be queried for data, or send data
    """

    def __init__(self, exchange: ExchangeType) -> None:
        self._exchange: ExchangeType = exchange

    def exchange(self) -> ExchangeType:
        return self._exchange

    @staticmethod
    def registerExchange(exchange_name: str, clazz: Type) -> None:
        _EXCHANGES[exchange_name] = clazz

    @staticmethod
    def exchanges(exchange: str = None) -> Union[Type, List[str]]:
        if exchange:
            if exchange not in _EXCHANGES:
                raise Exception(f"Unknown exchange type: {exchange}")
            return _EXCHANGES[exchange]
        return list(_EXCHANGES.keys())

    @abstractmethod
    async def connect(self) -> None:
        """connect to exchange. should be asynchronous.

        For OrderEntry-only, can just return None
        """

    async def lookup(self, instrument: Instrument) -> List[Instrument]:
        """lookup an instrument on the exchange"""
        return []

    # ****************** #
    # Inherited  methods #

    # From _MarketData
    #
    # async def tick(self):
    # def instruments(self):
    # def subscribe(self, instrument):

    # From _OrderEntry
    #
    # async def newOrder(self, order: Order):
    # def accounts(self) -> List:
    # ************************** #
