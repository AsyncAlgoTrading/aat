import sys
import os.path
from aat.common import _in_cpp


class TestOfflineCalculations:
    def setup_class(self):
        self._argv = sys.argv

    def teardown_class(self):
        sys.argv = self._argv

    def test_calculations(self):
        from aat.strategy.calculations import main

        sys.argv = [
            "aat.strategy.calculations",
            "--folder",
            os.path.join(os.path.dirname(__file__), "_aat_BACKTEST_test"),
            "--strategy",
            "MomentumStrategy-0",
            "--render",
            "False",
        ]

        if _in_cpp():
            # TODO
            return
        main()
