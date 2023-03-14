from collections import deque
from typing import Optional, Deque, Dict, List, Union
from aat.core import Order


class PriceLevelRO(object):
    """Readonly Price Level"""

    __slots__ = [
        "_price",
        "_volume",
        "_number_of_orders",
        "_orders",
    ]

    def __init__(
        self,
        price: float,
        volume: float,
        number_of_orders: int = 0,
        _orders: Optional[Deque[Order]] = None,
    ):
        self._price = price
        self._volume = volume
        self._number_of_orders = number_of_orders
        self._orders = _orders or deque()

    @property
    def price(self) -> float:
        return self._price

    @property
    def volume(self) -> float:
        return self._volume

    @property
    def orders(self) -> int:
        return self._number_of_orders

    def dict(self) -> Dict[str, Union[int, float]]:
        return {"price": self.price, "volume": self.volume, "orders": self.orders}

    def list(self) -> List[float]:
        return [self.price, self.volume]

    def __eq__(self, other: object) -> bool:
        if isinstance(other, list):
            return self.list() == other
        elif isinstance(other, dict):
            return self.dict() == other
        elif isinstance(other, PriceLevelRO):
            return (
                self.price == other.price
                and self.volume == other.volume
                and self.orders == other.orders
            )
        else:
            raise TypeError()
