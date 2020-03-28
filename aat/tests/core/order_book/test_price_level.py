from aat.core.order_book.price_level import _PriceLevel


class TestOrderBook:
    def test_price_level(self):
        # just instantiate, validate below
        pl = _PriceLevel(5.0, print)
        assert bool(pl) is False
