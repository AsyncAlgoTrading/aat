from collections import deque
from typing import Mapping, Type, Union, List, Dict
from .order import Order
from ...config import DataType, Side
from ...common import _in_cpp

try:
    from aat.binding import TradeCpp  # type: ignore
    _CPP = _in_cpp()
except ImportError:
    _CPP = False


def _make_cpp_trade(id, timestamp, maker_orders=None, taker_order=None):
    '''helper method to ensure all arguments are setup'''
    return TradeCpp(id, timestamp, maker_orders or deque(), taker_order)


class Trade(object):
    __slots__ = [
        "__id",
        "__type",
        "__price",
        "__volume",
        "__maker_orders",
        "__taker_order",

        # FIXME hide
        "__my_order",
        "__slippage",
        "__transaction_cost",
    ]

    # for convenience
    Types = DataType

    def __new__(cls, *args, **kwargs):
        if _CPP:
            return _make_cpp_trade(*args, **kwargs)
        return super(Trade, cls).__new__(cls)

    def __init__(self, volume, price, maker_orders, taker_order):
        self.__id = -1  # on construction, provide no ID until exchange assigns one
        self.__type = DataType.TRADE

        assert(isinstance(price, (float, int)))
        assert(isinstance(volume, (float, int)))
        assert(isinstance(taker_order, Order))
        # assert(len(maker_orders) > 0)  # not necessarily

        self.__price = price
        self.__volume = volume
        self.__maker_orders = maker_orders
        self.__taker_order = taker_order

        self.__my_order = None
        self.__slippage = 0.0
        self.__transaction_cost = 0.0

    # ******** #
    # Readonly #
    # ******** #
    @property
    def timestamp(self) -> int:
        return self.taker_order.timestamp

    @property
    def type(self):
        return self.__type

    @property
    def volume(self):
        return self.__volume

    @property
    def price(self):
        return self.__price

    @property
    def instrument(self):
        return self.taker_order.instrument

    @property
    def exchange(self):
        return self.taker_order.exchange

    @property
    def side(self) -> Side:
        return self.taker_order.side

    @property
    def notional(self):
        return self.price * self.volume

    # ***********#
    # Read/write #
    # ***********#
    @property
    def id(self) -> int:
        return self.__id

    @id.setter
    def id(self, id: int) -> None:
        assert isinstance(id, int)
        self.__id = id

    @property
    def maker_orders(self) -> List[Order]:
        # no setter
        return self.__maker_orders

    @property
    def taker_order(self) -> Order:
        return self.__taker_order

    @property
    def my_order(self) -> Order:
        return self.__my_order

    @my_order.setter
    def my_order(self, order: Order) -> None:
        assert isinstance(order, Order)
        self.__my_order = order

    def __repr__(self) -> str:
        return f'Trade( id={self.id}, timestamp={self.timestamp}, {self.volume}@{self.price}, \n\ttaker_order={self.taker_order},\n\tmaker_orders={self.maker_orders}, )'

    def __eq__(self, other) -> bool:
        assert isinstance(other, Trade)
        return self.id == other.id and \
            self.timestamp == other.timestamp

    def to_json(self) -> Mapping[str, Union[str, int, float]]:
        '''convert trade to flat json'''

        # Typings here to enforce flatness of json
        taker_order: Dict[str, Union[str, int, float]] = \
            {'taker_order.' + k: v for k, v in self.taker_order.to_json().items()}

        maker_orders: List[Dict[str, Union[str, int, float]]] = \
            [{'maker_order{}.' + k: v for k, v in order.to_json().items()} for i, order in enumerate(self.maker_orders)]

        ret: Dict[str, Union[str, int, float]] = \
            {'id': self.id, 'timestamp': self.timestamp,
             'price': self.price, 'volume': self.volume}

        # update with taker order dict
        ret.update(taker_order)

        # update with maker order dicts
        for maker_order in maker_orders:
            ret.update(maker_order)
        return ret

    @staticmethod
    def perspectiveSchema() -> Mapping[str, Type]:
        # FIXME
        # this varies from the json schema
        return {
            "id": int,
            "timestamp": int,
            "volume": float,
            "price": float,
        }
