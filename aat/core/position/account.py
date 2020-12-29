from typing import Mapping, Type, Dict, Tuple, List, Optional

from aat.core.exchange import ExchangeType

from .cpp import _CPP, _make_cpp_account
from .position import Position


class Account(object):
    __slots__ = ["__id", "__exchange", "__positions"]

    def __new__(cls: Type, *args: Tuple, **kwargs: Dict) -> "Account":
        if _CPP:
            return _make_cpp_account(*args, **kwargs)
        return super(Account, cls).__new__(cls)

    def __init__(
        self,
        id: str,
        exchange: ExchangeType,
        positions: Optional[List[Position]] = None,
    ) -> None:
        assert isinstance(exchange, ExchangeType)

        self.__id = id
        self.__exchange = exchange
        self.__positions = positions or []

    # ******** #
    # Readonly #
    # ******** #
    @property
    def id(self) -> str:
        return self.__id

    @property
    def exchange(self) -> ExchangeType:
        return self.__exchange

    @property
    def positions(self) -> List[Position]:
        return self.__positions

    # ***********#
    # Read/write #
    # ***********#
    def addPosition(self, position: Position) -> None:
        self.__positions.append(position)

    def json(self) -> dict:
        return {
            "id": self.id,
            "exchange": self.exchange.json(),
            "positions": [p.json() for p in self.positions],
        }

    @staticmethod
    def fromJson(jsn: dict) -> "Account":
        kwargs = {}
        kwargs["id"] = jsn["id"]
        kwargs["exchange"] = ExchangeType.fromJson(jsn["exchange"])
        kwargs["positions"] = [Position.fromJson(x) for x in jsn["positions"]]

        ret = Account(**kwargs)
        return ret

    @staticmethod
    def schema() -> Mapping[str, Type]:
        return {"id": str, "exchange": str}

    def __repr__(self) -> str:
        return f"Account(id={self.id}, exchange={self.exchange})"
