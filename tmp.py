from datetime import datetime
from aat.config import Side, DataType, OrderType, OrderFlag
from aat.core import Instrument, OrderBook, Order

_INSTRUMENT = Instrument('TE.ST')        

ob = OrderBook(_INSTRUMENT)

x = .5
while x < 10.0:
    side = Side.BUY if x <= 5 else Side.SELL
    ob.add(Order(id=1,
                timestamp=datetime.now().timestamp(),
                volume=1.0,
                price=x,
                side=side,
                type=DataType.ORDER,
                instrument=_INSTRUMENT,
                exchange=''))
    x += .5


assert ob.topOfBook()['bid'] == (5.0, 1.0)
assert ob.topOfBook()['ask'] == (5.5, 1.0)

print(ob)
assert ob.topOfBook() == {"bid": (5.0, 1.0), 'ask': (5.5, 1.0)}

data = Order(id=1,
            timestamp=datetime.now().timestamp(),
            volume=0.0,
            price=5.0,
            side=Side.SELL,
            type=DataType.ORDER,
            order_type=OrderType.STOP_MARKET,
            stop_target=Order(
                id=1,
                timestamp=datetime.now().timestamp(),
                volume=1.0,
                price=4.0,
                side=Side.SELL,
                type=DataType.ORDER,
                order_type=OrderType.MARKET,
                instrument=_INSTRUMENT,
                exchange=''
            ),
            instrument=_INSTRUMENT,
            exchange='')
print(ob)
ob.add(data)

data = Order(id=1,
            timestamp=datetime.now().timestamp(),
            volume=0.0,
            price=5.0,
            side=Side.SELL,
            type=DataType.ORDER,
            order_type=OrderType.STOP_LIMIT,
            stop_target=Order(
                id=1,
                timestamp=datetime.now().timestamp(),
                volume=0.5,
                price=5.0,
                side=Side.SELL,
                type=DataType.ORDER,
                instrument=_INSTRUMENT,
                exchange=''
            ),
            instrument=_INSTRUMENT,
            exchange='')
print(ob)
ob.add(data)

print(ob)
assert ob.topOfBook() == {"bid": (5.0, 1.0), "ask": (5.5, 1.0)}

data = Order(id=1,
            timestamp=datetime.now().timestamp(),
            volume=0.5,
            price=5.0,
            side=Side.SELL,
            type=DataType.ORDER,
            order_type=OrderType.LIMIT,
            instrument=_INSTRUMENT,
            exchange='')
print(ob)
ob.add(data)

print(ob)
assert ob.topOfBook() == {"bid": (4.5, 0.5), "ask": (5.0, 0.5)}
