from datetime import datetime
from aat.config import Side, DataType, OrderFlag, OrderType
from aat.core import Instrument, OrderBook, Order
from .helpers import _seed

_INSTRUMENT = Instrument('TE.ST')

class TestOrderFlagsTaker:
    def setup(self):
        self.ob = OrderBook(_INSTRUMENT)
        _seed(self.ob, _INSTRUMENT)
        assert self.ob.topOfBook() == {"bid": (5.0, 1.0), 'ask': (5.5, 1.0)}

    def test_fill_or_kill_market(self):
        data = Order(id=1,
                    timestamp=datetime.now().timestamp(),
                    volume=2.0,
                    price=5.0,
                    side=Side.SELL,
                    type=DataType.ORDER,
                    order_type=OrderType.MARKET,
                    flag=OrderFlag.FILL_OR_KILL,
                    instrument=_INSTRUMENT,
                    exchange='')
        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {"bid": (5.0, 1.0), "ask": (5.5, 1.0)}

        data = Order(id=1,
                    timestamp=datetime.now().timestamp(),
                    volume=2.0,
                    price=4.5,
                    side=Side.SELL,
                    type=DataType.ORDER,
                    order_type=OrderType.MARKET,
                    flag=OrderFlag.FILL_OR_KILL,
                    instrument=_INSTRUMENT,
                    exchange='')
        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {"bid": (4.0, 1.0), "ask": (5.5, 1.0)}

    def test_fill_or_kill_taker_limit(self):
        data = Order(id=1,
                    timestamp=datetime.now().timestamp(),
                    volume=2.0,
                    price=5.0,
                    side=Side.SELL,
                    type=DataType.ORDER,
                    order_type=OrderType.LIMIT,
                    flag=OrderFlag.FILL_OR_KILL,
                    instrument=_INSTRUMENT,
                    exchange='')
        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {"bid": (5.0, 1.0), "ask": (5.5, 1.0)}

        data = Order(id=1,
                    timestamp=datetime.now().timestamp(),
                    volume=2.0,
                    price=4.5,
                    side=Side.SELL,
                    type=DataType.ORDER,
                    order_type=OrderType.LIMIT,
                    flag=OrderFlag.FILL_OR_KILL,
                    instrument=_INSTRUMENT,
                    exchange='')
        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {"bid": (4.0, 1.0), "ask": (5.5, 1.0)}

    def test_all_or_none_market(self):
        data = Order(id=1,
                    timestamp=datetime.now().timestamp(),
                    volume=1.5,
                    price=5.0,
                    side=Side.SELL,
                    type=DataType.ORDER,
                    order_type=OrderType.MARKET,
                    flag=OrderFlag.ALL_OR_NONE,
                    instrument=_INSTRUMENT,
                    exchange='')
        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {"bid": (5.0, 1.0), "ask": (5.5, 1.0)}

        data = Order(id=1,
                    timestamp=datetime.now().timestamp(),
                    volume=0.5,
                    price=5.0,
                    side=Side.SELL,
                    type=DataType.ORDER,
                    order_type=OrderType.MARKET,
                    flag=OrderFlag.ALL_OR_NONE,
                    instrument=_INSTRUMENT,
                    exchange='')
        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {"bid": (5.0, 0.5), "ask": (5.5, 1.0)}

    def test_all_or_none_taker_limit(self):
        data = Order(id=1,
                    timestamp=datetime.now().timestamp(),
                    volume=1.5,
                    price=5.0,
                    side=Side.SELL,
                    type=DataType.ORDER,
                    order_type=OrderType.LIMIT,
                    flag=OrderFlag.ALL_OR_NONE,
                    instrument=_INSTRUMENT,
                    exchange='')
        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {"bid": (5.0, 1.0), "ask": (5.5, 1.0)}

        data = Order(id=1,
                    timestamp=datetime.now().timestamp(),
                    volume=0.5,
                    price=5.0,
                    side=Side.SELL,
                    type=DataType.ORDER,
                    order_type=OrderType.LIMIT,
                    flag=OrderFlag.ALL_OR_NONE,
                    instrument=_INSTRUMENT,
                    exchange='')
        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {"bid": (5.0, 0.5), "ask": (5.5, 1.0)}

    def test_immediate_or_cancel_market(self):
        data = Order(id=1,
                    timestamp=datetime.now().timestamp(),
                    volume=2.0,
                    price=5.0,
                    side=Side.SELL,
                    type=DataType.ORDER,
                    order_type=OrderType.MARKET,
                    flag=OrderFlag.IMMEDIATE_OR_CANCEL,
                    instrument=_INSTRUMENT,
                    exchange='')
        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {"bid": (4.5, 1.0), "ask": (5.5, 1.0)}

        data = Order(id=1,
                    timestamp=datetime.now().timestamp(),
                    volume=2.0,
                    price=4.0,
                    side=Side.SELL,
                    type=DataType.ORDER,
                    order_type=OrderType.MARKET,
                    flag=OrderFlag.IMMEDIATE_OR_CANCEL,
                    instrument=_INSTRUMENT,
                    exchange='')
        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {"bid": (3.5, 1.0), "ask": (5.5, 1.0)}

    def test_immediate_or_cancel_taker_limit(self):
        data = Order(id=1,
                    timestamp=datetime.now().timestamp(),
                    volume=2.0,
                    price=5.0,
                    side=Side.SELL,
                    type=DataType.ORDER,
                    order_type=OrderType.LIMIT,
                    flag=OrderFlag.IMMEDIATE_OR_CANCEL,
                    instrument=_INSTRUMENT,
                    exchange='')
        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {"bid": (4.5, 1.0), "ask": (5.5, 1.0)}

        data = Order(id=1,
                    timestamp=datetime.now().timestamp(),
                    volume=2.0,
                    price=4.0,
                    side=Side.SELL,
                    type=DataType.ORDER,
                    order_type=OrderType.LIMIT,
                    flag=OrderFlag.IMMEDIATE_OR_CANCEL,
                    instrument=_INSTRUMENT,
                    exchange='')
        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {"bid": (3.5, 1.0), "ask": (5.5, 1.0)}


class TestOrderFlagsMaker:
    def test_fill_or_kill_maker(self):
        self.ob = OrderBook(_INSTRUMENT)
        _seed(self.ob, _INSTRUMENT, OrderFlag.FILL_OR_KILL)
        assert self.ob.topOfBook() == {"bid": (5.0, 1.0), 'ask': (5.5, 1.0)}

        data = Order(id=1,
                    timestamp=datetime.now().timestamp(),
                    volume=0.5,
                    price=5.0,
                    side=Side.SELL,
                    type=DataType.ORDER,
                    order_type=OrderType.LIMIT,
                    instrument=_INSTRUMENT,
                    exchange='')
        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {"bid": (4.5, 1.0), "ask": (5.0, 0.5)}

        data = Order(id=1,
                    timestamp=datetime.now().timestamp(),
                    volume=1.5,
                    price=4.0,
                    side=Side.SELL,
                    type=DataType.ORDER,
                    order_type=OrderType.LIMIT,
                    instrument=_INSTRUMENT,
                    exchange='')
        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {"bid": (3.5, 1.0), "ask": (4.0, 0.5)}


    def test_all_or_none_maker(self):
        self.ob = OrderBook(_INSTRUMENT)
        _seed(self.ob, _INSTRUMENT, OrderFlag.ALL_OR_NONE)
        assert self.ob.topOfBook() == {"bid": (5.0, 1.0), 'ask': (5.5, 1.0)}


        data = Order(id=1,
                    timestamp=datetime.now().timestamp(),
                    volume=0.5,
                    price=5.0,
                    side=Side.SELL,
                    type=DataType.ORDER,
                    order_type=OrderType.LIMIT,
                    instrument=_INSTRUMENT,
                    exchange='')
        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {"bid": (4.5, 1.0), "ask": (5.0, 0.5)}

        data = Order(id=1,
                    timestamp=datetime.now().timestamp(),
                    volume=1.5,
                    price=4.0,
                    side=Side.SELL,
                    type=DataType.ORDER,
                    order_type=OrderType.LIMIT,
                    instrument=_INSTRUMENT,
                    exchange='')
        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {"bid": (3.5, 1.0), "ask": (4.0, 0.5)}

    def test_immediate_or_cancel_maker(self):
        self.ob = OrderBook(_INSTRUMENT)
        _seed(self.ob, _INSTRUMENT, OrderFlag.IMMEDIATE_OR_CANCEL)
        assert self.ob.topOfBook() == {"bid": (5.0, 1.0), 'ask': (5.5, 1.0)}

        data = Order(id=1,
                    timestamp=datetime.now().timestamp(),
                    volume=0.5,
                    price=5.0,
                    side=Side.SELL,
                    type=DataType.ORDER,
                    order_type=OrderType.LIMIT,
                    instrument=_INSTRUMENT,
                    exchange='')
        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {"bid": (4.5, 1.0), "ask": (5.5, 1.0)}
