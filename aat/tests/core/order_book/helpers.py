from aat.config import Side, OrderFlag, OrderType
from aat.core import Order, ExchangeType


def _seed(ob, instrument, flag=OrderFlag.NONE):
    x = 0.5
    while x < 10.0:
        side = Side.BUY if x <= 5 else Side.SELL
        order = Order(
            volume=1.0,
            price=x,
            side=side,
            instrument=instrument,
            exchange=ExchangeType(""),
            order_type=OrderType.LIMIT,
            flag=flag,
            id="1",
        )
        ob.add(order)
        x += 0.5
