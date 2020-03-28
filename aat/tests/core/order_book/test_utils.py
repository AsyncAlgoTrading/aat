from aat.core.order_book.utils import _insort


class TestUtils:
    def test_insort(self):
        a = [1, 2, 3]
        assert _insort(a, 1.5)
        assert a == [1, 1.5, 2, 3]
        assert _insort(a, 1.5) is False
