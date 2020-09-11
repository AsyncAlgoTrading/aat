from typing import Callable, List, Mapping, Optional

from .base import OrderBookBase
from ..exchange import ExchangeType
from ..models import Order
from ...config import Side


class OrderBookLite(OrderBookBase):
    '''A partial order book for clients of exchanges that don't
    provide order events but provide snapshots or overall state.

    Args:
        instrument (Instrument): the instrument for the book
        exchange_name (str): name of the exchange
        callback (Function): callback on events
    '''

    def __init__(self,
                 instrument,
                 exchange_name='',
                 callback: Callable = print):

        self._instrument = instrument
        self._exchange_name = exchange_name or ExchangeType('')
        self._callback = callback

        # reset levels
        self.reset()

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
