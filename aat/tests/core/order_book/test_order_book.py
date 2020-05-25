from datetime import datetime
from aat.core import Instrument, OrderBook, Order
from .helpers import _seed

_INSTRUMENT = Instrument('TE.ST')


class TestOrderBook:
    def test_order_book_init(self):
        ob = OrderBook(_INSTRUMENT)
        print(ob.topOfBook())
        assert ob.topOfBook()['bid'] == (0, 0)
        assert ob.topOfBook()['ask'] == (float('inf'), 0)

    def test_order_book_run(self):
        ob = OrderBook(_INSTRUMENT)
        _seed(ob, _INSTRUMENT)

        assert ob.topOfBook()['bid'] == (5.0, 1.0)
        assert ob.topOfBook()['ask'] == (5.5, 1.0)

        data = Order(id=1,
                     timestamp=datetime.now().timestamp(),
                     volume=5.0,
                     price=4.5,
                     side=Order.Sides.SELL,
                     instrument=_INSTRUMENT)
        ob.add(data)

        print(ob)
        assert ob.topOfBook() == {"bid": (4.0, 1.0), "ask": (4.5, 3.0)}
        print(ob.levels(3))
        assert ob.levels(3) == {'bid': [(4.0, 1.0), (0.5, 1.0), (4.0, 1.0), (3.5, 1.0)], 'ask': [(4.5, 3.0), (4.5, 3.0), (5.5, 1.0), (6.0, 1.0)]}

        data = Order(id=1,
                     timestamp=datetime.now().timestamp(),
                     volume=4.0,
                     price=5.5,
                     side=Order.Sides.BUY,
                     instrument=_INSTRUMENT)
        ob.add(data)

        print(ob)
        assert ob.topOfBook() == {"bid": (4.0, 1.0), "ask": (6.0, 1.0)}
        print(ob.levels(3))
        assert ob.levels(3) == {'bid': [(4.0, 1.0), (0.5, 1.0), (4.0, 1.0), (3.5, 1.0)], 'ask': [(6.0, 1.0), (6.0, 1.0), (6.5, 1.0), (7.0, 1.0)]}

    def test_order_book_clearing_order(self):
        ob = OrderBook(_INSTRUMENT)

        _seed(ob, _INSTRUMENT)

        assert ob.topOfBook()['bid'] == (5.0, 1.0)
        assert ob.topOfBook()['ask'] == (5.5, 1.0)

        data = Order(id=1,
                     timestamp=datetime.now().timestamp(),
                     volume=100.0,
                     price=0.0,
                     side=Order.Sides.SELL,
                     instrument=_INSTRUMENT)
        ob.add(data)

        print(ob)
        print(ob.topOfBook())
        assert ob.topOfBook() == {"bid": (0.0, 0.0), "ask": (0.0, 90.0)}
        print(ob.levels(3))
        assert ob.levels(3) == {'bid': [(0, 0)], 'ask': [(0.0, 90.0), (0.0, 90.0), (5.5, 1.0), (6.0, 1.0)]}
