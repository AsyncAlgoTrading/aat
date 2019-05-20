import pandas as pd


class TestBacktest:
    def setup(self):
        from ..config import BacktestConfig
        self.config = BacktestConfig()
        df = pd.DataFrame([{'volume': '100',
                            'close': '1',
                            'timestamp': '1558296780000',
                            'pair': 'USDBTC'
                            }])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index(['timestamp', 'pair'])
        self.test_line = df.iloc[0]

    def teardown(self):
        pass
        # teardown() after each test method

    @classmethod
    def setup_class(cls):
        from ..callback import Callback

        class CallbackTester(Callback):
            def __init__(self):
                self._onTrade = False
                self._onReceived = False
                self._onOpen = False
                self._onDone = False
                self._onChange = False
                self._onError = False
                self._onAnalyze = False
                self._onHalt = False
                self._onContinue = False

            def onTrade(self, data):
                self._onTrade = True

            def onReceived(self, data):
                self._onReceived = True

            def onOpen(self, data):
                self._onOpen = True

            def onDone(self, data):
                self._onDone = True

            def onChange(self, data):
                self._onChange = True

            def onError(self, data):
                self._onError = True

            def onAnalyze(self, data):
                self._onAnalyze = True

            def onHalt(self, data):
                self._onHalt = True

            def onContinue(self, data):
                self._onContinue = True

        cls.demo_callback = CallbackTester

    @classmethod
    def teardown_class(cls):
        pass
        # teardown_class() after any methods in this class

    def test_init(self):
        from ..backtest import Backtest
        b = Backtest(self.config)
        assert b

    def test_receive(self):
        from ..backtest import Backtest, line_to_data

        b = Backtest(self.config)
        cb = self.demo_callback()

        b.registerCallback(cb)
        b.receive(line_to_data(self.test_line))
        assert cb._onTrade
