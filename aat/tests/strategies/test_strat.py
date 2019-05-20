from mock import patch, MagicMock


class TestSMACrossesStrategy:
    def setup(self):
        pass
        # setup() before each test method

    def teardown(self):
        pass
        # teardown() after each test method

    @classmethod
    def setup_class(cls):
        pass
        # setup_class() before any methods in this class

    @classmethod
    def teardown_class(cls):
        pass
        # teardown_class() after any methods in this class

    def test_sma_strat_init(self):
        from ...strategies.test_strat import TestStrategy
        s = TestStrategy()
        assert s

        # unused
        s.onChange(None)
        s.onContinue(None)
        s.onDone(None)
        s.onHalt(None)
        s.onOpen(None)
        s.onReceived(None)

        m = MagicMock()
        resp = s.slippage(m)
        resp = s.transactionCost(m)

    def test_sma_buy(self):
        from ...strategies.test_strat import TestStrategy
        s = TestStrategy()

        s.onBuy(MagicMock())
        s.onSell(MagicMock())
