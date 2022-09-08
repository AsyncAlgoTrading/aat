from datetime import datetime


class TestCommon:
    def test_merge(self):
        from aat.common import _merge

        l1 = [
            (1, datetime(2020, 1, 1)),
            (1, datetime(2020, 1, 2)),
            (2, datetime(2020, 1, 3)),
            (2, datetime(2020, 1, 4)),
            (3, datetime(2020, 1, 5)),
            (3, datetime(2020, 1, 6)),
            (4, datetime(2020, 1, 7)),
            (4, datetime(2020, 1, 8)),
            (3, datetime(2020, 1, 9)),
            (3, datetime(2020, 1, 20)),
            (2, datetime(2020, 1, 21)),
            (2, datetime(2020, 1, 22)),
            (1, datetime(2020, 1, 23)),
            (1, datetime(2020, 1, 24)),
            (0, datetime(2020, 1, 25)),
            (0, datetime(2020, 1, 26)),
            (-1, datetime(2020, 1, 27)),
            (-1, datetime(2020, 1, 28)),
            (0, datetime(2020, 1, 29)),
            (0, datetime(2020, 1, 30)),
        ]

        l2 = [
            (1, datetime(2020, 1, 5)),
            (1, datetime(2020, 1, 6)),
            (1, datetime(2020, 1, 7)),
            (1, datetime(2020, 1, 8)),
            (-2, datetime(2020, 1, 9)),
            (-2, datetime(2020, 1, 10)),
            (-2, datetime(2020, 1, 11)),
            (-2, datetime(2020, 1, 12)),
            (-2, datetime(2020, 1, 13)),
            (-2, datetime(2020, 1, 14)),
            (2, datetime(2020, 1, 22)),
            (2, datetime(2020, 1, 23)),
            (2, datetime(2020, 1, 24)),
            (2, datetime(2020, 1, 25)),
            (2, datetime(2020, 1, 26)),
            (1, datetime(2020, 1, 29)),
            (1, datetime(2020, 1, 30)),
        ]

        combined = [
            (1, datetime(2020, 1, 1)),
            (1, datetime(2020, 1, 2)),
            (2, datetime(2020, 1, 3)),
            (2, datetime(2020, 1, 4)),
            (4, datetime(2020, 1, 5)),
            (4, datetime(2020, 1, 6)),
            (5, datetime(2020, 1, 7)),
            (5, datetime(2020, 1, 8)),
            (1, datetime(2020, 1, 9)),
            (1, datetime(2020, 1, 10)),
            (1, datetime(2020, 1, 11)),
            (1, datetime(2020, 1, 12)),
            (1, datetime(2020, 1, 13)),
            (1, datetime(2020, 1, 14)),
            (1, datetime(2020, 1, 20)),
            (0, datetime(2020, 1, 21)),
            (4, datetime(2020, 1, 22)),
            (3, datetime(2020, 1, 23)),
            (3, datetime(2020, 1, 24)),
            (2, datetime(2020, 1, 25)),
            (2, datetime(2020, 1, 26)),
            (1, datetime(2020, 1, 27)),
            (1, datetime(2020, 1, 28)),
            (1, datetime(2020, 1, 29)),
            (1, datetime(2020, 1, 30)),
        ]

        ret = _merge(l1, l2)

        assert ret == combined
