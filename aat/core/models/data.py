from pydantic import BaseModel
from typing import Dict, Mapping, Union, Type
from ...config import Side, DataType
from ..instrument import Instrument


class Data(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    id: int = 0
    timestamp: int
    volume: float
    price: float
    side: Side

    type: DataType
    instrument: Instrument

    # maybe specific
    exchange: str = ''
    filled: float = 0.0

    def __eq__(self, other) -> bool:
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
             'exchange': self.exchange}

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
