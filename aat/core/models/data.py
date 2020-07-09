import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Mapping, Union, Type

from ..exchange import ExchangeType
from ..instrument import Instrument
from ...common import _in_cpp
from ...config import Side, DataType

try:
    from aat.binding import DataCpp
    _CPP = _in_cpp()

except ImportError:
    logging.critical("Could not load C++ extension")
    _CPP = False


def _make_cpp_data(id, timestamp, volume, price, side, instrument, exchange, filled=0.0):
    '''helper method to ensure all arguments are setup'''
    return DataCpp(id, timestamp, volume, price, side, instrument, exchange, filled)


@dataclass
class Data:
    def __new__(cls, *args, **kwargs):
        if _CPP:
            return _make_cpp_data(*args, **kwargs)
        return super(Data, cls).__new__(cls)

    # internal
    id: int = field(default=0, repr=False)
    timestamp: datetime = field(default_factory=datetime.now)

    # public
    volume: float
    price: float
    side: Side
    type: DataType
    instrument: Instrument
    exchange: ExchangeType = field(default=ExchangeType(''))

    filled: float = 0.0

    def __eq__(self, other) -> bool:
        assert isinstance(other, Data)
        return (self.price == other.price) and \
            (self.instrument == other.instrument) and \
            (self.side == other.side)

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
