from abc import ABC, abstractmethod
from typing import Dict, Iterator, List, Optional, Tuple, Union

from .price_level import PriceLevelRO
from ..data import Order
from ...config import Side


class OrderBookBase(ABC):
    @abstractmethod
    def reset(self) -> None:
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
    def topOfBook(self) -> Dict[Side, PriceLevelRO]:
        pass

    @abstractmethod
    def spread(self) -> float:
        pass

    @abstractmethod
    def level(self, level: int = 0, price: float = None) -> Tuple:
        pass

    @abstractmethod
    def levels(self, levels: int = 0) -> Dict[Side, List[PriceLevelRO]]:
        pass

    @abstractmethod
    def bids(
        self, levels: int = 0
    ) -> Union[PriceLevelRO, List[Optional[PriceLevelRO]]]:
        pass

    @abstractmethod
    def asks(
        self, levels: int = 0
    ) -> Union[PriceLevelRO, List[Optional[PriceLevelRO]]]:
        pass

    @abstractmethod
    def __iter__(self) -> Iterator[Order]:
        pass
