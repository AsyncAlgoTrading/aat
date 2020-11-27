from typing import Dict, Union


class PriceLevelRO(object):
    """Readonly Price Level"""

    __slots__ = [
        "_price",
        "_volume",
        "_number_of_orders",
    ]

    def __init__(self, price: float, volume: float, number_of_orders: int):
        self._price = price
        self._volume = volume
        self._number_of_orders = number_of_orders

    @property
    def price(self) -> float:
        return self._price

    @property
    def volume(self) -> float:
        return self._volume

    @property
    def orders(self) -> int:
        return self._number_of_orders

    def toDict(self) -> Dict[str, Union[int, float]]:
        return {"price": self.price, "volume": self.volume, "orders": self.orders}
