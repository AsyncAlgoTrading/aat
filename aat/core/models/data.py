import logging
from pydantic import BaseModel, validator
from datetime import datetime
from typing import Mapping, Union, Type

from ...config import Side, DataType
from ..instrument import Instrument
from ..exchange import ExchangeType
from ...common import _in_cpp

try:
    from aat.binding import DataCpp
    _CPP = _in_cpp()
    _base = object if _CPP else BaseModel

except ImportError:
    logging.critical("Could not load C++ extension")
    _CPP = False
    _base = BaseModel


def _make_cpp_data(id, timestamp, volume, price, side, instrument, exchange, filled=0.0):
    '''helper method to ensure all arguments are setup'''
    return DataCpp(id, timestamp, volume, price, side, instrument, exchange, filled)


class Data(_base):
    def __new__(cls, *args, **kwargs):
        if _CPP:
            return _make_cpp_data(*args, **kwargs)
        return super(Data, cls).__new__(cls)

    class Config:
        arbitrary_types_allowed = True

    # internal
    id: int = 0
    timestamp: datetime = None

    # public
    volume: float
    price: float
    side: Side
    type: DataType
    instrument: Instrument
    exchange: ExchangeType = ExchangeType('')

    filled: float = 0.0

    @validator("timestamp", always=True)
    def _set_timestamp_if_unset(cls, v):
        if v is None:
            return datetime.now()
        assert isinstance(v, datetime)
        return v

    def __eq__(self, other) -> bool:
        assert isinstance(other, Data)
        return (self.price == other.price) and \
            (self.instrument == other.instrument) and \
            (self.side == other.side)

    def __str__(self):
        return f'<{self.instrument}-{self.volume}@{self.price}-{self.type}-{self.exchange}-{self.side}>'

    def __lt__(self, other) -> bool:
        return self.price < other.price

    def to_json(self) -> Mapping[str, Union[str, int, float]]:
        return \
            {'id': self.id,
             'timestamp': self.timestamp,
             'volume': self.volume,
             'price': self.price,
             'side': self.side.value,
             'type': self.type.value,
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
            "type": str,
            "instrument": str,
            "exchange": str,
        }
