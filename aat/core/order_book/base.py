from abc import ABC, abstractmethod
from typing import List, Mapping, Optional

from ...config import Side
from ..models import Order


class OrderBookBase(ABC):
    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def add(self, order: Order) -> None:
        pass

    @abstractmethod
    def cancel(self, order: Order) -> None:
        pass

    @abstractmethod
    def change(self, order: Order) -> None:
        pass

    @abstractmethod
    def find(self, order: Order) -> Optional[Order]:
        pass

    @abstractmethod
    def topOfBook(self) -> Mapping[Side, List[float]]:
        pass

    @abstractmethod
    def spread(self) -> float:
        pass

    @abstractmethod
    def level(self, level: int = 0, price: float = None):
        pass

    @abstractmethod
    def levels(self, levels=0):
        pass

    @abstractmethod
    def __iter__(self):
        pass
