from abc import abstractmethod
from typing import List

from aat.core import ExchangeType, Instrument

from .base.market_data import _MarketData
from .base.order_entry import _OrderEntry


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
