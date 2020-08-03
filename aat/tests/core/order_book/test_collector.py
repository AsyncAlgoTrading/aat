from aat.core.order_book.collector import _Collector


class TestCollector:
    def test_collector(self):
        c = _Collector(lambda *args: print(args))
        assert c
