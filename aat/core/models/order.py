from pydantic import validator
from .data import Data
from ...config import DataType, OrderFlag, OrderType


class Order(Data):
    type: DataType = DataType.ORDER
    order_type: OrderType = OrderType.LIMIT
    flag: OrderFlag = OrderFlag.NONE
    filled: float = 0.0
    stop_target: Data = None
    notional: float = 0.0

    @validator("stop_target")
    def _assert_stop_target_not_stop(cls, v, values, **kwargs):
        assert isinstance(v, Order)
        assert v.order_type not in (OrderType.STOP_LIMIT, OrderType.STOP_MARKET)
        if values['order_type'] == OrderType.STOP_LIMIT:
            assert v.order_type == OrderType.LIMIT
        if values['order_type'] == OrderType.STOP_MARKET:
            assert v.order_type == OrderType.MARKET
        return v

    def __str__(self):
        return f'<{self.instrument}-{self.volume}@{self.price}-{self.exchange}-{self.side}>'

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
