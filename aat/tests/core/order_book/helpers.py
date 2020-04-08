from datetime import datetime
from aat.config import Side, DataType, OrderFlag, OrderType
from aat.core import Order, Exchange


def _seed(ob, instrument, flag=OrderFlag.NONE):
    x = .5
    while x < 10.0:
        side = Side.BUY if x <= 5 else Side.SELL
        ob.add(Order(id=1,
                     timestamp=datetime.now().timestamp(),
                     volume=1.0,
                     price=x,
                     side=side,
                     type=DataType.ORDER,
                     order_type=OrderType.LIMIT,
                     flag=flag,
                     instrument=instrument,
                     exchange=Exchange("")))
        x += .5
