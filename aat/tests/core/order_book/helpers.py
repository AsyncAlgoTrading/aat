from datetime import datetime
from aat.config import Side, DataType
from aat.core import Order


def _seed(ob, instrument):
    x = .5
    while x < 10.0:
        side = Side.BUY if x <= 5 else Side.SELL
        ob.add(Order(id=1,
                     timestamp=datetime.now().timestamp(),
                     volume=1.0,
                     price=x,
                     side=side,
                     type=DataType.ORDER,
                     instrument=instrument,
                     exchange=''))
        x += .5
