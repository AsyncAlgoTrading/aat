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
        from ...strategies.backtest import CustomStrategy
        from ...enums import Side
        s = CustomStrategy(5)
        assert s

        # unused
        s.onChange(None)
        s.onContinue(None)
        s.onDone(None)
        s.onHalt(None)
        s.onOpen(None)
        s.onReceived(None)

        m = MagicMock()
        m.price = 10000
        m.volume = 1
        m.side = Side.BUY
        m.slippage = 0
        m.transaction_cost = 0

        resp = s.slippage(m)
        assert m.slippage == 1.0
        assert m.price == 10001.0

        resp = s.transactionCost(m)
        assert m.transaction_cost == 25.0025
        assert m.price == 10026.0025

        m.price = 10000
        m.volume = 1
        m.side = Side.SELL
        m.slippage = 0
        m.transaction_cost = 0
        resp = s.slippage(m)
        assert m.slippage == -1.0
        assert m.price == 9999.0

        resp = s.transactionCost(m)
        assert m.transaction_cost <= -24.9974 and m.transaction_cost >= -24.9976
        assert m.price == 9974.0025

    def test_sma_buy(self):
        from ...strategies.backtest import CustomStrategy
        s = CustomStrategy(5)

        s.onBuy(MagicMock())
        s.onSell(MagicMock())
