import logging
from datetime import datetime
from typing import Mapping, Union, Type

from ..exchange import ExchangeType
from ..instrument import Instrument
from ...common import _in_cpp, id_generator
from ...config import DataType

_ID_GENERATOR = id_generator()

try:
    from aat.binding import DataCpp  # type: ignore
    _CPP = _in_cpp()

except ImportError:
    logging.critical("Could not load C++ extension")
    _CPP = False


def _make_cpp_data(id, timestamp, instrument, exchange, data):
    '''helper method to ensure all arguments are setup'''
    return DataCpp(id, timestamp, instrument, exchange, data)


class Data(object):
    __slots__ = [
        "__id",
        "__timestamp",
        "__type",
        "__instrument",
        "__exchange",
        "__data"
    ]

    def __new__(cls, *args, **kwargs):
        if _CPP:
            return _make_cpp_data(*args, **kwargs)
        return super(Data, cls).__new__(cls)

    def __init__(self, instrument=None, exchange=ExchangeType("")):
        self.__id = _ID_GENERATOR()
        self.__timestamp = datetime.now()

        assert instrument is None or isinstance(instrument, Instrument)
        assert isinstance(exchange, ExchangeType)
        self.__type = DataType.DATA
        self.__instrument = instrument
        self.__exchange = exchange

    # ******** #
    # Readonly #
    # ******** #
    @property
    def id(self) -> int:
        return self.__id

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

    def __repr__(self) -> str:
        return f'Data( id={self.id}, timestamp={self.timestamp}, instrument={self.instrument}, exchange={self.exchange})'

    def __eq__(self, other) -> bool:
        assert isinstance(other, Data)
        return self.id == other.id

    def toJson(self) -> Mapping[str, Union[str, int, float]]:
        return \
            {'id': self.id,
             'timestamp': self.timestamp,
             'type': self.type.value,
             'instrument': str(self.instrument),
             'exchange': str(self.exchange)}

    @staticmethod
    def perspectiveSchema() -> Mapping[str, Type]:
        return {
            "id": int,
            "timestamp": int,
            "type": str,
            "instrument": str,
            "exchange": str,
        }
