import aat.binding as ab
from aat.binding import Side, DataType
from datetime import datetime
from random import random, choice, randint

inst = ab.InstrumentCpp("TE.ST")
exc = ab.ExchangeTypeCpp("TEST")

orderbook = ab.OrderBookCpp(inst, exc)

start = 1.0
end = 10.0
mid = 5.0
id = 1

while start < end:
    o = ab.OrderCpp(0, 0., 1.0, 1.0, ab.Side.BUY, inst, exc, 0.0, ab.OrderType.LIMIT, ab.OrderFlag.NONE, None, 0.0)
    side = Side.BUY if start <= mid else Side.SELL
    increment = choice((.1, .2, .5))
    orderbook.add(ab.OrderCpp(id,
                              datetime.now().timestamp(),
                              round(randint(1, 10)/5, 1),
                              round(start, 2),
                              side,
                              inst,
                              exc,
                              0.0,
                              ab.OrderType.LIMIT,
                              ab.OrderFlag.NONE,
                              None,
                              0.0))
    print(orderbook)
    start = round(start + increment, 2)

print(orderbook)
