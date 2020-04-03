from collections import deque
from pydantic import validator
from .data import Data
from .order import Order
from ...config import DataType


class Trade(Data):
    type: DataType = DataType.TRADE
    maker_orders: deque
    taker_order: Order

    _slippage: float = 0.0
    _transaction_cost: float = 0.0

    def slippage(self):
        '''the amount of slippage of the order'''
        return 0.0

    def transaction_cost(self):
        '''any transaction costs incurred on the order'''
        return 0.0

    @validator("maker_orders")
    def _assert_maker_orders(cls, v):
        assert len(v) > 0
        return v

    def __str__(self):
        return f'<{self.instrument}-{self.volume:.2f}@{self.price:.2f}-{self.exchange}>'

    def to_json(self):
        ret = {}
        ret['id'] = self.id
        ret['timestamp'] = self.timestamp
        ret['volume'] = self.volume
        ret['price'] = self.price
        ret['side'] = self.side.value
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
            "instrument": str,
            "exchange": str,
        }
