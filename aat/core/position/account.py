from typing import Mapping, Type

from .position import Position
from ..exchange import ExchangeType
from ...common import _in_cpp

try:
    from aat.binding import AccountCpp  # type: ignore

    _CPP = _in_cpp()
except ImportError:
    _CPP = False


class Account(object):
    __slots__ = ["__id", "__exchange", "__positions"]

    def __new__(cls, *args, **kwargs):
        if _CPP:
            return AccountCpp(*args, **kwargs)
        return super(Account, cls).__new__(cls)

    def __init__(self, id, exchange, positions=None):
        assert isinstance(exchange, ExchangeType)

        self.__id = id
        self.__exchange = exchange
        self.__positions = positions or []

    # ******** #
    # Readonly #
    # ******** #
    @property
    def id(self):
        return self.__id

    @property
    def exchange(self):
        return self.__exchange

    @property
    def positions(self):
        return self.__positions

    # ***********#
    # Read/write #
    # ***********#
    def addPosition(self, position):
        self.__positions.append(position)

    def toJson(self):
        return {
            "id": self.id,
            "exchange": self.exchange.toJson(),
            "positions": [p.toJson() for p in self.positions],
        }

    @staticmethod
    def fromJson(jsn):
        kwargs = {}
        kwargs["id"] = jsn["id"]
        kwargs["exchange"] = ExchangeType.fromJson(jsn["exchange"])
        kwargs["positions"] = [Position.fromJson(x) for x in jsn["positions"]]

        ret = Account(**kwargs)
        return ret

    @staticmethod
    def perspectiveSchema() -> Mapping[str, Type]:
        return {"id": str, "exchange": str}

    def __repr__(self):
        return f"Account(id={self.id}, exchange={self.exchange})"
