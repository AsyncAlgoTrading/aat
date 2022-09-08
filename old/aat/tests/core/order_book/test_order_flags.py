from aat.config import Side
from aat.core import Instrument, OrderBook, Order
from .helpers import _seed

_INSTRUMENT = Instrument("TE.ST")


class TestOrderFlagsTaker:
    def setup(self):
        self.ob = OrderBook(_INSTRUMENT)
        _seed(self.ob, _INSTRUMENT)
        assert self.ob.topOfBook() == {Side.BUY: [5.0, 1.0], Side.SELL: [5.5, 1.0]}

    def test_fill_or_kill_market(self):
        data = Order(
            volume=2.0,
            price=5.0,
            side=Order.Sides.SELL,
            order_type=Order.Types.MARKET,
            flag=Order.Flags.FILL_OR_KILL,
            instrument=_INSTRUMENT,
            id="1",
        )
        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {Side.BUY: [5.0, 1.0], Side.SELL: [5.5, 1.0]}

        data = Order(
            volume=2.0,
            price=4.5,
            side=Order.Sides.SELL,
            order_type=Order.Types.MARKET,
            flag=Order.Flags.FILL_OR_KILL,
            instrument=_INSTRUMENT,
            id="1",
        )
        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {Side.BUY: [4.0, 1.0], Side.SELL: [5.5, 1.0]}

    def test_fill_or_kill_taker_limit(self):
        data = Order(
            volume=2.0,
            price=5.0,
            side=Order.Sides.SELL,
            order_type=Order.Types.LIMIT,
            flag=Order.Flags.FILL_OR_KILL,
            instrument=_INSTRUMENT,
            id="1",
        )

        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {Side.BUY: [5.0, 1.0], Side.SELL: [5.5, 1.0]}

        data = Order(
            volume=2.0,
            price=4.5,
            side=Order.Sides.SELL,
            order_type=Order.Types.LIMIT,
            flag=Order.Flags.FILL_OR_KILL,
            instrument=_INSTRUMENT,
            id="1",
        )
        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {Side.BUY: [4.0, 1.0], Side.SELL: [5.5, 1.0]}

    def test_all_or_none_market(self):
        data = Order(
            volume=1.5,
            price=5.0,
            side=Order.Sides.SELL,
            order_type=Order.Types.MARKET,
            flag=Order.Flags.ALL_OR_NONE,
            instrument=_INSTRUMENT,
            id="1",
        )
        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {Side.BUY: [5.0, 1.0], Side.SELL: [5.5, 1.0]}

        data = Order(
            volume=0.5,
            price=5.0,
            side=Order.Sides.SELL,
            order_type=Order.Types.MARKET,
            flag=Order.Flags.ALL_OR_NONE,
            instrument=_INSTRUMENT,
            id="1",
        )
        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {Side.BUY: [5.0, 0.5], Side.SELL: [5.5, 1.0]}

    def test_all_or_none_taker_limit(self):
        data = Order(
            volume=1.5,
            price=5.0,
            side=Order.Sides.SELL,
            order_type=Order.Types.LIMIT,
            flag=Order.Flags.ALL_OR_NONE,
            instrument=_INSTRUMENT,
            id="1",
        )
        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {Side.BUY: [5.0, 1.0], Side.SELL: [5.5, 1.0]}

        data = Order(
            volume=0.5,
            price=5.0,
            side=Order.Sides.SELL,
            order_type=Order.Types.LIMIT,
            flag=Order.Flags.ALL_OR_NONE,
            instrument=_INSTRUMENT,
            id="1",
        )
        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {Side.BUY: [5.0, 0.5], Side.SELL: [5.5, 1.0]}

    def test_immediate_or_cancel_market(self):
        data = Order(
            volume=2.0,
            price=5.0,
            side=Order.Sides.SELL,
            order_type=Order.Types.MARKET,
            flag=Order.Flags.IMMEDIATE_OR_CANCEL,
            instrument=_INSTRUMENT,
            id="1",
        )
        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {Side.BUY: [4.5, 1.0], Side.SELL: [5.5, 1.0]}

        data = Order(
            volume=2.0,
            price=4.0,
            side=Order.Sides.SELL,
            order_type=Order.Types.MARKET,
            flag=Order.Flags.IMMEDIATE_OR_CANCEL,
            instrument=_INSTRUMENT,
            id="1",
        )
        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {Side.BUY: [3.5, 1.0], Side.SELL: [5.5, 1.0]}

    def test_immediate_or_cancel_taker_limit(self):
        data = Order(
            volume=2.0,
            price=5.0,
            side=Order.Sides.SELL,
            order_type=Order.Types.LIMIT,
            flag=Order.Flags.IMMEDIATE_OR_CANCEL,
            instrument=_INSTRUMENT,
            id="1",
        )
        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {Side.BUY: [4.5, 1.0], Side.SELL: [5.5, 1.0]}

        data = Order(
            volume=2.0,
            price=4.0,
            side=Order.Sides.SELL,
            order_type=Order.Types.LIMIT,
            flag=Order.Flags.IMMEDIATE_OR_CANCEL,
            instrument=_INSTRUMENT,
            id="1",
        )
        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {Side.BUY: [3.5, 1.0], Side.SELL: [5.5, 1.0]}


class TestOrderFlagsMaker:
    def test_fill_or_kill_maker(self):
        self.ob = OrderBook(_INSTRUMENT)
        _seed(self.ob, _INSTRUMENT, Order.Flags.FILL_OR_KILL)
        assert self.ob.topOfBook() == {Side.BUY: [5.0, 1.0], Side.SELL: [5.5, 1.0]}

        data = Order(
            volume=0.5,
            price=5.0,
            side=Order.Sides.SELL,
            order_type=Order.Types.LIMIT,
            instrument=_INSTRUMENT,
            id="1",
        )
        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {Side.BUY: [4.5, 1.0], Side.SELL: [5.0, 0.5]}

        data = Order(
            volume=1.5,
            price=4.0,
            side=Order.Sides.SELL,
            order_type=Order.Types.LIMIT,
            instrument=_INSTRUMENT,
            id="1",
        )
        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {Side.BUY: [3.5, 1.0], Side.SELL: [4.0, 0.5]}

    def test_all_or_none_maker(self):
        self.ob = OrderBook(_INSTRUMENT)
        _seed(self.ob, _INSTRUMENT, Order.Flags.ALL_OR_NONE)
        assert self.ob.topOfBook() == {Side.BUY: [5.0, 1.0], Side.SELL: [5.5, 1.0]}

        data = Order(
            volume=0.5,
            price=5.0,
            side=Order.Sides.SELL,
            order_type=Order.Types.LIMIT,
            instrument=_INSTRUMENT,
            id="1",
        )
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {Side.BUY: [4.5, 1.0], Side.SELL: [5.0, 0.5]}

        data = Order(
            volume=1.5,
            price=4.0,
            side=Order.Sides.SELL,
            order_type=Order.Types.LIMIT,
            instrument=_INSTRUMENT,
            id="1",
        )
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {Side.BUY: [3.5, 1.0], Side.SELL: [4.0, 0.5]}

    def test_immediate_or_cancel_maker(self):
        self.ob = OrderBook(_INSTRUMENT)
        _seed(self.ob, _INSTRUMENT, Order.Flags.IMMEDIATE_OR_CANCEL)
        assert self.ob.topOfBook() == {Side.BUY: [5.0, 1.0], Side.SELL: [5.5, 1.0]}

        data = Order(
            volume=0.5,
            price=5.0,
            side=Order.Sides.SELL,
            order_type=Order.Types.LIMIT,
            instrument=_INSTRUMENT,
            id="1",
        )
        print(self.ob)
        self.ob.add(data)

        print(self.ob.topOfBook())
        assert self.ob.topOfBook() == {Side.BUY: [4.5, 1.0], Side.SELL: [5.5, 1.0]}
