from queue import Queue
from typing import Callable, List, Mapping, Optional

from aat.core import ExchangeType, Order, Instrument, Event
from aat.config import Side

from ..price_level import PriceLevelRO
from ..base import OrderBookBase


class OrderBookLite(OrderBookBase):
    """A partial order book for clients of exchanges that don't
    provide order events but provide snapshots or overall state.

    Args:
        instrument (Instrument): the instrument for the book
        exchange_name (str): name of the exchange
        callback (Function): callback on events
    """

    def __init__(
        self,
        instrument: Instrument,
        exchange_name: str = "",
        callback: Optional[Callable] = None,
    ):

        self._instrument = instrument
        self._exchange_name = exchange_name or ExchangeType("")
        self._callback = callback or self._push

        # reset levels and collector
        self.reset()

        # default callback is to enqueue
        self._queue: "Queue[Event]" = Queue()

    @property
    def queue(self) -> Queue:
        return self._queue

    def _push(self, event) -> None:
        self._queue.put(event)

    def add(self, order: Order) -> None:
        raise NotImplementedError()

    def cancel(self, order: Order) -> None:
        raise NotImplementedError()

    def change(self, order: Order) -> None:
        raise NotImplementedError()

    def find(self, order: Order) -> Optional[Order]:
        raise NotImplementedError()

    def topOfBook(self) -> Mapping[Side, List[float]]:
        raise NotImplementedError()

    def spread(self) -> float:
        raise NotImplementedError()

    def level(self, level: int = 0, price: float = None):
        raise NotImplementedError()

    def levels(self, levels=0):
        raise NotImplementedError()

    def __iter__(self):
        raise NotImplementedError()

    @staticmethod
    def fromPriceLevels(
        self, price_levels: Mapping[Side, List[PriceLevelRO]]
    ) -> "OrderBookLite":
        pass
