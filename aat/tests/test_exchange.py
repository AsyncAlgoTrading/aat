class TestExchange:
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

    def test_init(self):
        from ..config import ExchangeConfig
        from ..exchange import Exchange

        ec = ExchangeConfig()

        try:
            e = Exchange(ec)
            assert e
            assert False
        except:
            assert True
