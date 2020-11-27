from typing import Mapping, Type

from aat.core.exchange import ExchangeType

from .cpp import _CPP, _make_cpp_account
from .position import Position


class Account(object):
    __slots__ = ["__id", "__exchange", "__positions"]

    def __new__(cls, *args, **kwargs):
        if _CPP:
            return _make_cpp_account(*args, **kwargs)
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

    def json(self):
        return {
            "id": self.id,
            "exchange": self.exchange.json(),
            "positions": [p.json() for p in self.positions],
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
    def schema() -> Mapping[str, Type]:
        return {"id": str, "exchange": str}

    def __repr__(self):
        return f"Account(id={self.id}, exchange={self.exchange})"
