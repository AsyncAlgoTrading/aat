class TestDefine:
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

    def test_exchange_endpoint(self):
        from ..define import EXCHANGE_MARKET_DATA_ENDPOINT
        from ..enums import ExchangeType, TradingType

        assert EXCHANGE_MARKET_DATA_ENDPOINT(ExchangeType.COINBASE, TradingType.SANDBOX) \
            == 'wss://ws-feed-public.sandbox.pro.coinbase.com'
        assert EXCHANGE_MARKET_DATA_ENDPOINT(ExchangeType.COINBASE, TradingType.LIVE) \
            == 'wss://ws-feed.pro.coinbase.com'
        assert EXCHANGE_MARKET_DATA_ENDPOINT(ExchangeType.GEMINI, TradingType.SANDBOX) \
            == 'wss://api.sandbox.gemini.com/v1/marketdata/%s?heartbeat=true'
        assert EXCHANGE_MARKET_DATA_ENDPOINT(ExchangeType.GEMINI, TradingType.LIVE) \
            == 'wss://api.gemini.com/v1/marketdata/%s?heartbeat=true'
        assert EXCHANGE_MARKET_DATA_ENDPOINT(ExchangeType.KRAKEN, TradingType.SANDBOX) \
            == 'wss://ws-beta.kraken.com'
        assert EXCHANGE_MARKET_DATA_ENDPOINT(ExchangeType.KRAKEN, TradingType.LIVE) \
            == 'wss://ws.kraken.com'
        assert EXCHANGE_MARKET_DATA_ENDPOINT(ExchangeType.POLONIEX, TradingType.SANDBOX) \
            == ''
        assert EXCHANGE_MARKET_DATA_ENDPOINT(ExchangeType.POLONIEX, TradingType.LIVE) \
            == 'wss://api2.poloniex.com'
