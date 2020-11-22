from aat.config import Side
from aat.core import Instrument, OrderBook, Order
from .helpers import _seed


_INSTRUMENT = Instrument("TE.ST")


class TestMarketOrder:
    def test_order_book_market_order(self):
        ob = OrderBook(_INSTRUMENT)

        _seed(ob, _INSTRUMENT)

        assert ob.topOfBook()[Side.BUY] == [5.0, 1.0]
        assert ob.topOfBook()[Side.SELL] == [5.5, 1.0]

        data = Order(
            volume=100.0,
            price=0.0,
            side=Order.Sides.SELL,
            order_type=Order.Types.MARKET,
            instrument=_INSTRUMENT,
        )
        ob.add(data)

        print(ob)
        print(ob.topOfBook())
        assert ob.topOfBook() == {Side.BUY: [0, 0], Side.SELL: [5.5, 1.0]}
        print(ob.levels(3))
        assert ob.levels(3) == {
            Side.BUY: [[0, 0], [0, 0], [0, 0]],
            Side.SELL: [[5.5, 1.0], [6.0, 1.0], [6.5, 1.0]],
        }


class TestStopLoss:
    def test_stop_limit(self):
        ob = OrderBook(_INSTRUMENT)

        _seed(ob, _INSTRUMENT)

        assert ob.topOfBook()[Side.BUY] == [5.0, 1.0]
        assert ob.topOfBook()[Side.SELL] == [5.5, 1.0]

        print(ob)
        assert ob.topOfBook() == {Side.BUY: [5.0, 1.0], Side.SELL: [5.5, 1.0]}

        data = Order(
            volume=0.0,
            price=5.0,
            side=Order.Sides.SELL,
            order_type=Order.Types.STOP,
            stop_target=Order(
                volume=1.0,
                price=4.0,
                side=Order.Sides.SELL,
                order_type=Order.Types.MARKET,
                instrument=_INSTRUMENT,
            ),
            instrument=_INSTRUMENT,
        )
        print(ob)
        ob.add(data)

        data = Order(
            volume=0.0,
            price=5.0,
            side=Order.Sides.SELL,
            order_type=Order.Types.STOP,
            stop_target=Order(
                volume=0.5,
                price=5.0,
                side=Order.Sides.SELL,
                instrument=_INSTRUMENT,
                order_type=Order.Types.LIMIT,
            ),
            instrument=_INSTRUMENT,
        )
        print(ob)
        ob.add(data)

        print(ob.topOfBook())
        assert ob.topOfBook() == {Side.BUY: [5.0, 1.0], Side.SELL: [5.5, 1.0]}

        data = Order(
            volume=0.5,
            price=5.0,
            side=Order.Sides.SELL,
            order_type=Order.Types.LIMIT,
            instrument=_INSTRUMENT,
        )
        print(ob)
        ob.add(data)

        print(ob.topOfBook())
        assert ob.topOfBook() == {Side.BUY: [4.5, 0.5], Side.SELL: [5.0, 0.5]}

    def test_stop_market(self):
        ob = OrderBook(_INSTRUMENT)

        _seed(ob, _INSTRUMENT)

        assert ob.topOfBook()[Side.BUY] == [5.0, 1.0]
        assert ob.topOfBook()[Side.SELL] == [5.5, 1.0]

        print(ob)
        assert ob.topOfBook() == {Side.BUY: [5.0, 1.0], Side.SELL: [5.5, 1.0]}

        data = Order(
            volume=0.0,
            price=5.0,
            side=Order.Sides.SELL,
            order_type=Order.Types.STOP,
            stop_target=Order(
                volume=0.5,
                price=4.5,
                side=Order.Sides.SELL,
                instrument=_INSTRUMENT,
                order_type=Order.Types.LIMIT,
            ),
            instrument=_INSTRUMENT,
        )
        print(ob)
        ob.add(data)

        print(ob.topOfBook())
        assert ob.topOfBook() == {Side.BUY: [5.0, 1.0], Side.SELL: [5.5, 1.0]}

        data = Order(
            volume=0.5,
            price=5.0,
            side=Order.Sides.SELL,
            order_type=Order.Types.LIMIT,
            instrument=_INSTRUMENT,
        )
        print(ob)
        ob.add(data)

        print(ob.topOfBook())
        assert ob.topOfBook() == {Side.BUY: [4.5, 1.0], Side.SELL: [5.5, 1.0]}
