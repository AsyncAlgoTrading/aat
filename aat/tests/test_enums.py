class TestEnums:
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

    def test_trading_type(self):
        from ..enums import TradingType
        t0 = TradingType.NONE
        t1 = TradingType.SANDBOX
        t2 = TradingType.LIVE
        t3 = TradingType.BACKTEST
        assert t0 == TradingType.NONE
        assert t1 == TradingType.SANDBOX
        assert t2 == TradingType.LIVE
        assert t3 == TradingType.BACKTEST
        assert t0 == TradingType('NONE')
        assert t1 == TradingType('SANDBOX')
        assert t2 == TradingType('LIVE')
        assert t3 == TradingType('BACKTEST')

    def test_exchange_type(self):
        from ..enums import ExchangeType, ExchangeType_from_string
        t0 = ExchangeType.NONE
        t1 = ExchangeType.COINBASE
        t2 = ExchangeType.GEMINI
        t3 = ExchangeType.KRAKEN
        t4 = ExchangeType.POLONIEX
        assert t0 == ExchangeType.NONE
        assert t1 == ExchangeType.COINBASE
        assert t2 == ExchangeType.GEMINI
        assert t3 == ExchangeType.KRAKEN
        assert t4 == ExchangeType.POLONIEX
        assert t0 == ExchangeType_from_string('NONE')
        assert t1 == ExchangeType_from_string('COINBASE')
        assert t2 == ExchangeType_from_string('GEMINI')
        assert t3 == ExchangeType_from_string('KRAKEN')
        assert t4 == ExchangeType_from_string('POLONIEX')

    def test_tick_type(self):
        from ..enums import TickType, TickType_from_string
        try:
            t0 = TickType_from_string('test')
            assert False
        except ValueError:
            pass

    def test_currency_type(self):
        from ..enums import CurrencyType
        t0 = CurrencyType.USD
        t1 = CurrencyType.BTC
        t2 = CurrencyType.ETH
        t3 = CurrencyType.LTC
        assert t0 == CurrencyType.USD
        assert t1 == CurrencyType.BTC
        assert t2 == CurrencyType.ETH
        assert t3 == CurrencyType.LTC
        assert t0 == CurrencyType('USD')
        assert t1 == CurrencyType('BTC')
        assert t2 == CurrencyType('ETH')
        assert t3 == CurrencyType('LTC')

    def test_side(self):
        from ..enums import Side
        t0 = Side.NONE
        t1 = Side.BUY
        t2 = Side.SELL
        assert t0 == Side.NONE
        assert t1 == Side.BUY
        assert t2 == Side.SELL
        assert t0 == Side('NONE')
        assert t1 == Side('BUY')
        assert t2 == Side('SELL')

    def test_order_type(self):
        from ..enums import OrderType
        t0 = OrderType.NONE
        t1 = OrderType.MARKET
        t2 = OrderType.LIMIT
        assert t0 == OrderType.NONE
        assert t1 == OrderType.MARKET
        assert t2 == OrderType.LIMIT
        assert t0 == OrderType('NONE')
        assert t1 == OrderType('MARKET')
        assert t2 == OrderType('LIMIT')

    def test_order_sub_type(self):
        from ..enums import OrderSubType
        t0 = OrderSubType.NONE
        t1 = OrderSubType.POST_ONLY
        t2 = OrderSubType.FILL_OR_KILL
        # t3 = OrderSubType.ALL_OR_NOTHING
        assert t0 == OrderSubType.NONE
        assert t1 == OrderSubType.POST_ONLY
        assert t2 == OrderSubType.FILL_OR_KILL
        # assert t3 == OrderSubType.ALL_OR_NOTHING
        assert t0 == OrderSubType('NONE')
        assert t1 == OrderSubType('POST_ONLY')
        assert t2 == OrderSubType('FILL_OR_KILL')
        # assert t3 == OrderSubType(3)
