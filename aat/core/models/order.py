from .data import Data
from ...config import DataType, OrderFlag


class Order(Data):
    type: DataType = DataType.ORDER
    flag: OrderFlag = OrderFlag.NONE
    filled: float = 0.0

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
