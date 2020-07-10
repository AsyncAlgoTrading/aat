from datetime import datetime
from typing import Mapping, Union, Type

from ..exchange import ExchangeType
from ..instrument import Instrument
from ...common import _in_cpp
from ...config import DataType, OrderFlag, OrderType, Side


try:
    from aat.binding import OrderCpp
    _CPP = _in_cpp()
except ImportError:
    _CPP = False


def _make_cpp_order(id, timestamp, volume, price, side, instrument, exchange=ExchangeType(""), filled=0.0, notional=0.0, order_type=OrderType.LIMIT, flag=OrderFlag.NONE, stop_target=None):
    '''helper method to ensure all arguments are setup'''
    return OrderCpp(id, timestamp, volume, price, side, instrument, exchange, filled, order_type, flag, stop_target, notional)


class Order(object):
    __slots__ = [
        "__id",
        "__timestamp",
        "__type",
        "__instrument",
        "__exchange",
        "__volume",
        "__price",
        "__notional",
        "__filled",
        "__side",
        "__order_type",
        "__flag",
        "__stop_target",
    ]

    # for convenience
    Types = OrderType
    Sides = Side
    Flags = OrderFlag

    def __new__(cls, *args, **kwargs):
        if _CPP:
            return _make_cpp_order(*args, **kwargs)
        return super(Order, cls).__new__(cls)

    def __init__(self, volume, price, side, instrument=None, exchange=ExchangeType(""), notional=0.0, order_type=OrderType.LIMIT, flag=OrderFlag.NONE, stop_target=None):
        self.__id = -1  # on construction, provide no ID until exchange assigns one
        self.__timestamp = datetime.now()
        self.__type = DataType.ORDER

        assert instrument is None or isinstance(instrument, Instrument)
        assert isinstance(exchange, ExchangeType)
        self.__instrument = instrument
        self.__exchange = exchange

        assert isinstance(volume, (int, float))
        assert isinstance(price, (int, float))
        assert isinstance(side, Side)
        assert isinstance(notional, (int, float))
        assert isinstance(order_type, OrderType)
        assert isinstance(flag, OrderFlag)
        assert stop_target is None or (isinstance(stop_target, Order) and order_type == OrderType.STOP)
        self.__volume = volume
        self.__price = price
        self.__side = side
        self.__notional = notional
        self.__order_type = order_type
        self.__flag = flag
        self.__stop_target = stop_target

        self.__filled = 0.0

    # TODO
    # @validator("notional")
    # def _assert_notional_set_correct(cls, v, values, **kwargs) -> float:
    #     if values['order_type'] == OrderType.MARKET:
    #         return v
    #     return values['price'] * values['volume']

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
    def instrument(self):
        return self.__instrument

    @property
    def exchange(self):
        return self.__exchange

    @property
    def price(self):
        return self.__price

    @property
    def side(self):
        return self.__side

    @property
    def notional(self):
        return self.__notional

    @property
    def order_type(self):
        return self.__order_type

    @property
    def flag(self):
        return self.__flag

    @property
    def stop_target(self):
        return self.__stop_target

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
    def volume(self):
        return self.__volume

    @volume.setter
    def volume(self, volume):
        assert isinstance(volume, (int, float))
        assert volume > self.filled
        self.__volume = volume

    @property
    def filled(self):
        return self.__filled

    @filled.setter
    def filled(self, filled):
        assert isinstance(filled, (int, float))
        self.__filled = filled

    def __repr__(self):
        return f'Order( instrument={self.instrument}, {self.volume}@{self.price}, exchange={self.exchange}, side={self.side})'

    def __eq__(self, other) -> bool:
        assert isinstance(other, Order)
        return self.id == other.id and \
            self.instrument == other.instrument and \
            self.price == other.price and \
            self.volume == other.volume and \
            self.notional == other.notional and \
            self.filled == other.filled

    def to_json(self) -> Mapping[str, Union[str, int, float]]:
        return \
            {'id': self.id,
                'timestamp': self.timestamp,
                'volume': self.volume,
                'price': self.price,
                'side': self.side.value,
                'instrument': str(self.instrument),
                'exchange': str(self.exchange)}

    @staticmethod
    def perspectiveSchema() -> Mapping[str, Type]:
        return {
            "id": int,
            "timestamp": int,
            "volume": float,
            "price": float,
            "side": str,
            "instrument": str,
            "exchange": str,
        }
