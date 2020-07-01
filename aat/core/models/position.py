from pydantic import BaseModel
from typing import List
from .trade import Trade
from ..exchange import ExchangeType
from ..instrument import Instrument
from ...common import _in_cpp

try:
    from aat.binding import PositionCpp
    _CPP = _in_cpp()
except ImportError:
    _CPP = False


class Position(BaseModel):
    def __new__(cls, *args, **kwargs):
        if _CPP:
            return PositionCpp(*args, **kwargs)
        return super(Position, cls).__new__(cls)

    class Config:
        arbitrary_types_allowed = True

    size: float = 0.0
    notional: float = 0.0
    price: float = 0.0
    instrument: Instrument
    exchange: ExchangeType = ExchangeType('')

    pnl: float = 0.0
    unrealizedPnl: float = 0.0
    trades: List[Trade] = []

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'P<{self.instrument}-{self.price}-{self.size}-{self.notional}-{self.pnl}-{self.unrealizedPnl}-{self.exchange}>'
