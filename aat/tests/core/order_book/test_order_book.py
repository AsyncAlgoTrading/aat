from datetime import datetime
from aat.config import Side, DataType
from aat.core import Instrument, OrderBook, Order
from aat.core.order_book.utils import _insort
from aat.core.order_book.price_level import _PriceLevel

_INSTRUMENT = Instrument('TE.ST')


class TestUtils:
    def test_insort(self):
        a = [1, 2, 3]
        assert _insort(a, 1.5)
        assert a == [1, 1.5, 2, 3]
        assert _insort(a, 1.5) is False


class TestOrderBook:
    def test_price_level(self):
        # just instantiate, validate below
        pl = _PriceLevel(5.0, print)
        assert bool(pl) is False

    def test_order_book_init(self):
        ob = OrderBook(_INSTRUMENT)
        print(ob.topOfBook())
        assert ob.topOfBook()['bid'] == (0, 0)
        assert ob.topOfBook()['ask'] == (float('inf'), 0)

    def test_order_book_run(self):
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

        data = Order(id=1,
                     timestamp=datetime.now().timestamp(),
                     volume=5.0,
                     price=4.5,
                     side=Side.SELL,
                     type=DataType.ORDER,
                     instrument=_INSTRUMENT,
                     exchange='')
        ob.add(data)

        print(ob)
        assert ob.topOfBook() == {"bid": (4.0, 1.0), "ask": (4.5, 3.0)}
        print(ob.levels(3))
        assert ob.levels(3) == {'bid': [(4.0, 1.0), (0.5, 1.0), (4.0, 1.0), (3.5, 1.0)], 'ask': [(4.5, 3.0), (4.5, 3.0), (5.5, 1.0), (6.0, 1.0)]}

        data = Order(id=1,
                     timestamp=datetime.now().timestamp(),
                     volume=4.0,
                     price=5.5,
                     side=Side.BUY,
                     type=DataType.ORDER,
                     instrument=_INSTRUMENT,
                     exchange='')
        ob.add(data)

        print(ob)
        assert ob.topOfBook() == {"bid": (4.0, 1.0), "ask": (6.0, 1.0)}
        print(ob.levels(3))
        assert ob.levels(3) == {'bid': [(4.0, 1.0), (0.5, 1.0), (4.0, 1.0), (3.5, 1.0)], 'ask': [(6.0, 1.0), (6.0, 1.0), (6.5, 1.0), (7.0, 1.0)]}

    def test_order_book_market_order(self):
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

        data = Order(id=1,
                     timestamp=datetime.now().timestamp(),
                     volume=100.0,
                     price=0.0,
                     side=Side.SELL,
                     type=DataType.ORDER,
                     instrument=_INSTRUMENT,
                     exchange='')
        ob.add(data)

        print(ob)
        assert ob.topOfBook() == {"bid": (0.0, 0.0), "ask": (4.5, 3.0)}
        print(ob.levels(3))
        assert ob.levels(3) == {'bid': [], 'ask': [(4.5, 3.0), (4.5, 3.0), (5.5, 1.0), (6.0, 1.0)]}
