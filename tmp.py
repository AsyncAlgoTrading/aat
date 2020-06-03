# import aat.binding as ab
# from aat.config import Side, DataType, EventType, OrderType, OrderFlag
# from aat.core import Order, Event
# from datetime import datetime
# from random import random, choice, randint

# inst = ab.InstrumentCpp("TE.ST")
# exc = ab.ExchangeTypeCpp("TEST")

# orderbook = ab.OrderBookCpp(inst, exc)

# start = 1.0
# end = 10.0
# mid = 5.0
# id = 1

# while start < end:
#     o = Order(0, datetime.now(), 1.0, 1.0, Side.BUY, inst, exc, 0.0, OrderType.LIMIT, OrderFlag.NONE, None, 0.0)
#     side = Side.BUY if start <= mid else Side.SELL
#     increment = choice((.1, .2, .5))
#     orderbook.add(Order(id,
#                         datetime.now(),
#                         round(randint(1, 10)/5, 1),
#                         round(start, 2),
#                         side,
#                         inst,
#                         exc,
#                         0.0,
#                         OrderType.LIMIT,
#                         OrderFlag.NONE,
#                         None,
#                         0.0))
#     print(orderbook)
#     start = round(start + increment, 2)

# print(orderbook)



# Event(EventType.OPEN, o)






from datetime import datetime
from aat.config import Side
from aat.core import Instrument, OrderBook, Order
from aat.tests.core.order_book.helpers import _seed

_INSTRUMENT = Instrument('TE.ST')

ob = OrderBook(_INSTRUMENT)

_seed(ob, _INSTRUMENT)

assert ob.topOfBook()[Side.BUY] == [5.0, 1.0]
assert ob.topOfBook()[Side.SELL] == [5.5, 1.0]

print(ob)
assert ob.topOfBook() == {Side.BUY: [5.0, 1.0], Side.SELL: [5.5, 1.0]}

data = Order(id=1,
                timestamp=datetime.now(),
                volume=0.0,
                price=5.0,
                side=Order.Sides.SELL,
                order_type=Order.Types.STOP,
                stop_target=Order(
                    id=1,
                    timestamp=datetime.now(),
                    volume=0.5,
                    price=4.5,
                    side=Order.Sides.SELL,
                    instrument=_INSTRUMENT
                ),
                instrument=_INSTRUMENT)
print(ob)
ob.add(data)

print(ob.topOfBook())
assert ob.topOfBook() == {Side.BUY: [5.0, 1.0], Side.SELL: [5.5, 1.0]}

data = Order(id=1,
             timestamp=datetime.now(),
             volume=0.5,
             price=5.0,
             side=Order.Sides.SELL,
             order_type=Order.Types.LIMIT,
             instrument=_INSTRUMENT)
print(ob)
ob.add(data)

print(ob.topOfBook())
assert ob.topOfBook() == {Side.BUY: [4.5, 1.0], Side.SELL: [5.5, 1.0]}
