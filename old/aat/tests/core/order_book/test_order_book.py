from aat.config import Side
from aat.core import Instrument, OrderBook, Order
from .helpers import _seed

_INSTRUMENT = Instrument("TE.ST")


class TestOrderBook:
    def test_order_book_init(self):
        ob = OrderBook(_INSTRUMENT)
        print(ob.topOfBook())
        assert ob.topOfBook()[Side.BUY] == [0, 0]
        assert ob.topOfBook()[Side.SELL] == [float("inf"), 0]

    def test_order_book_run(self):
        ob = OrderBook(_INSTRUMENT)
        _seed(ob, _INSTRUMENT)

        assert ob.topOfBook()[Side.BUY] == [5.0, 1.0]
        assert ob.topOfBook()[Side.SELL] == [5.5, 1.0]

        data = Order(
            volume=5.0,
            price=4.5,
            side=Order.Sides.SELL,
            instrument=_INSTRUMENT,
            order_type=Order.Types.LIMIT,
        )
        ob.add(data)

        print(ob)
        assert ob.topOfBook() == {Side.BUY: [4.0, 1.0], Side.SELL: [4.5, 3.0]}
        print(ob.levels(3))
        assert ob.levels(3) == {
            Side.BUY: [[4.0, 1.0], [3.5, 1.0], [3.0, 1.0]],
            Side.SELL: [[4.5, 3.0], [5.5, 1.0], [6.0, 1.0]],
        }

        data = Order(
            volume=4.0,
            price=5.5,
            side=Order.Sides.BUY,
            instrument=_INSTRUMENT,
            order_type=Order.Types.LIMIT,
        )
        ob.add(data)

        print(ob)
        assert ob.topOfBook() == {Side.BUY: [4.0, 1.0], Side.SELL: [6.0, 1.0]}
        print(ob.levels(3))
        assert ob.levels(3) == {
            Side.BUY: [[4.0, 1.0], [3.5, 1.0], [3.0, 1.0]],
            Side.SELL: [[6.0, 1.0], [6.5, 1.0], [7.0, 1.0]],
        }

    def test_order_book_clearing_order(self):
        ob = OrderBook(_INSTRUMENT)

        _seed(ob, _INSTRUMENT)

        assert ob.topOfBook()[Side.BUY] == [5.0, 1.0]
        assert ob.topOfBook()[Side.SELL] == [5.5, 1.0]

        data = Order(
            volume=100.0,
            price=0.0,
            side=Order.Sides.SELL,
            instrument=_INSTRUMENT,
            order_type=Order.Types.LIMIT,
        )
        ob.add(data)

        print(ob)
        print(ob.topOfBook())
        assert ob.topOfBook() == {Side.BUY: [0.0, 0.0], Side.SELL: [0.0, 90.0]}
        print(ob.levels(3))
        assert ob.levels(3) == {
            Side.BUY: [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0]],
            Side.SELL: [[0.0, 90.0], [5.5, 1.0], [6.0, 1.0]],
        }

    # def test_order_book_iter(self):
    #     ob = OrderBook(Instrument('TEST'),
    #                    ExchangeType(""))

    #     orders = [Order(10 + i,
    #                     5,
    #                     Side.BUY,
    #                     Instrument('TEST'),
    #                     ExchangeType(""),
    #                     0.0,
    #                     OrderType.LIMIT,
    #                     OrderFlag.NONE,
    #                     None) for i in range(100)]

    #     for o in orders:  # This causes a segfault
    #         ob.add(o)

    #     for o, op in zip(orders, ob):
    #         assert o == op
