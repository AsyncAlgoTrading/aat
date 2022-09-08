from aat.core.order_book.price_level import _PriceLevel
from aat.core.order_book.collector import _Collector


class TestOrderBook:
    def test_price_level(self):
        # just instantiate, validate below
        pl = _PriceLevel(5.0, _Collector())
        assert bool(pl) is False

    # def test_price_level_iter(self):
    #     pl = _PriceLevel(5, _Collector())
    #     orders = [Order(10 + i, 5, Side.BUY, Instrument('TEST'), ExchangeType(""), 0.0, OrderType.LIMIT, OrderFlag.NONE, None) for i in range(2)]

    #     for o in orders:  # This causes a segfault
    #         pl.add(o)

    #     for o, op in zip(orders, pl):
    #         assert o == op
