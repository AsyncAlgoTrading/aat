from pydantic import BaseModel
from typing import List
from .trade import Trade
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

    # timestamp: int
    size: float = 0.0
    notional: float = 0.0
    pnl: float = 0.0
    trades: List[Trade] = []

    def __str__(self):
        return f'<{self.size}-{self.notional}>'
