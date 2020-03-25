from pydantic import BaseModel
from typing import Any
from ...config import Side, DataType, EventType
from ..instrument import Instrument


class Data(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    id: int
    timestamp: int
    volume: float
    price: float
    side: Side

    type: DataType
    instrument: Instrument

    # maybe specific
    exchange: str
    filled: float = 0.0
    sequence: int = -1

    def __eq__(self, other):
        return (self.price == other.price) and \
               (self.instrument == other.instrument) and \
               (self.side == other.side)

    def __str__(self):
        return f'<{self.instrument}-{self.volume}@{self.price}-{self.type}-{self.exchange}-{self.side}>'

    def __lt__(self, other):
        return self.price < other.price

    def to_json(self):
        ret = {}
        ret['id'] = self.id
        ret['timestamp'] = self.timestamp
        ret['volume'] = self.volume
        ret['price'] = self.price
        ret['side'] = self.side.value
        ret['type'] = self.type.value
        ret['instrument'] = str(self.instrument)
        ret['exchange'] = self.exchange
        return ret

    @staticmethod
    def schema():
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