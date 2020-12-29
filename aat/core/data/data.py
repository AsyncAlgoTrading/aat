from datetime import datetime
from typing import Mapping, Union, Type, Optional, Any, cast

from .cpp import _CPP, _make_cpp_data
from ..exchange import ExchangeType
from ..instrument import Instrument
from ...common import id_generator
from ...config import DataType

_ID_GENERATOR = id_generator()


class Data(object):
    __slots__ = [
        "__id",
        "__timestamp",
        "__type",
        "__instrument",
        "__exchange",
        "__data",
    ]

    def __new__(cls, *args, **kwargs):  # type: ignore
        if _CPP:
            return _make_cpp_data(*args, **kwargs)
        return super(Data, cls).__new__(cls)

    def __init__(
        self,
        instrument: Optional[Instrument] = None,
        exchange: ExchangeType = ExchangeType(""),
        data: dict = {},
        **kwargs: Union[int, datetime],
    ) -> None:
        self.__id: int = cast(int, kwargs.get("id", _ID_GENERATOR()))
        self.__timestamp: datetime = cast(
            datetime, kwargs.get("timestamp", datetime.now())
        )

        assert instrument is None or isinstance(instrument, Instrument)
        assert isinstance(exchange, ExchangeType)
        self.__type = DataType.DATA
        self.__instrument = instrument
        self.__exchange = exchange
        self.__data = data

    # ******** #
    # Readonly #
    # ******** #
    @property
    def id(self) -> int:
        return self.__id

    @property
    def timestamp(self) -> datetime:
        return self.__timestamp

    @property
    def type(self) -> DataType:
        return self.__type

    @property
    def instrument(self) -> Optional[Instrument]:
        return self.__instrument

    @property
    def exchange(self) -> ExchangeType:
        return self.__exchange

    @property
    def data(self) -> Any:
        return self.__data

    def __repr__(self) -> str:
        return f"Data( id={self.id}, timestamp={self.timestamp}, instrument={self.instrument}, exchange={self.exchange})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Data):
            raise TypeError()
        return self.id == other.id

    def json(self, flat: bool = False) -> Mapping[str, Union[str, int, float]]:
        if flat:
            # TODO
            raise NotImplementedError()

        return {
            "id": self.id,
            "timestamp": self.timestamp.timestamp(),
            "type": self.type.value,
            "instrument": str(self.instrument),
            "exchange": str(self.exchange),
        }

    @staticmethod
    def schema() -> Mapping[str, Type]:
        return {
            "id": int,
            "timestamp": int,
            "type": str,
            "instrument": str,
            "exchange": str,
        }
