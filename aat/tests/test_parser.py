import os
import os.path


class TestRisk:
    def setup(self):
        from ..config import RiskConfig
        from ..risk import Risk

        rc = RiskConfig()
        rc.max_risk = 100.0
        rc.max_drawdown = 100.0
        rc.total_funds = 100.0

        self.risk = Risk(rc)

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

    def test_config_file(self):

        from ..parser import parse_file_config
        import tempfile

        t = tempfile.NamedTemporaryFile('w', delete=False)
        t.write('''[general]
verbose=1
print=0
TradingType=simulation

[exchange]
exchanges=coinbase
currency_pairs=BTCUSD,ETHUSD,LTCUSD,BCHUSD,ETHBTC,LTCBTC,BCHBTC

[strategy]
strategies =
    aat.strategies.test_strat.TestStrategy

[risk]
max_drawdown = 100.0
max_risk = 100.0
total_funds = 10.0
''')
        t.close()

        print(t.name)
        x = parse_file_config(t.name)
        assert x

        os.remove(t.name)
