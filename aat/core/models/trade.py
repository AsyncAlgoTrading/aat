from collections import deque
from datetime import datetime
from typing import Mapping, Type, Union
from .data import Data
from .order import Order
from ...config import DataType
from ...common import _in_cpp

try:
    from aat.binding import TradeCpp
    _CPP = _in_cpp()
except ImportError:
    _CPP = False


def _make_cpp_trade(id, timestamp, maker_orders=None, taker_order=None):
    '''helper method to ensure all arguments are setup'''
    return TradeCpp(id, timestamp, maker_orders or deque(), taker_order)


class Trade(Data):
    __slots__ = [
        "__id",
        "__timestamp",
        "__type",
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

    def __init__(self, maker_orders, taker_order):
        self.__id = -1  # on construction, provide no ID until exchange assigns one
        self.__timestamp = datetime.now()
        self.__type = DataType.TRADE

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
        return self.__timestamp

    @property
    def type(self):
        return self.__type

    @property
    def volume(self):
        return self.taker_order.volume

    @property
    def price(self):
        # FIXME calculate actual VWAP taking into account slippage/txncost
        return self.taker_order.price

    @property
    def instrument(self):
        return self.taker_order.instrument

    @property
    def exchange(self):
        return self.taker_order.exchange

    @property
    def side(self):
        return self.taker_order.side

    @property
    def notional(self):
        return self.taker_order.price * self.taker_order.volume

    # ***********#
    # Read/write #
    # ***********#
    @property
    def id(self) -> int:
        return self.__id

    @id.setter
    def id(self, id):
        assert isinstance(id, int)
        self.__id = id

    @property
    def maker_orders(self):
        # no setter
        return self.__maker_orders

    @property
    def taker_order(self):
        return self.__taker_order

    @property
    def my_order(self):
        return self.__my_order

    @my_order.setter
    def my_order(self, order):
        assert isinstance(order, Order)
        self.__my_order = order

    def __repr__(self):
        return f'Trade( id={self.id}, timestamp{self.timestamp}, maker_orders={len(self.maker_orders)}, taker_order={self.taker_order})'

    def __eq__(self, other) -> bool:
        assert isinstance(other, Trade)
        return self.id == other.id and \
            self.timestamp == other.timestamp

    def to_json(self) -> Mapping[str, Union[str, int, float]]:
        return \
            {'id': self.id,
             'timestamp': self.timestamp,
             'taker_order': self.taker_order.to_json(),
             'maker_orders': [order.to_json() for order in self.maker_orders()]}

    @staticmethod
    def perspectiveSchema() -> Mapping[str, Type]:
        # FIXME
        # this varies from the json schema
        return {
            "id": int,
            "timestamp": int,
        }
