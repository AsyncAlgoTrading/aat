from mock import patch


class TestMain:
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

    def test_parse_command_line(self):
        from ..main import parse_command_line_config
        from ..enums import TradingType

        argv = ['', '--live', '--exchanges=coinbase']
        ret = parse_command_line_config(argv)
        assert ret.type == TradingType.LIVE

        argv = ['', '--sandbox', '--exchanges=coinbase']
        ret = parse_command_line_config(argv)
        assert ret.type == TradingType.SANDBOX

        argv = ['', '--backtest', '--exchanges=coinbase']
        ret = parse_command_line_config(argv)
        assert ret.type == TradingType.BACKTEST

        argv = ['', '--live', '--print', '--exchanges=coinbase']
        ret = parse_command_line_config(argv)
        assert ret.print

    def test_main(self):
        from ..main import main
        with patch('aat.main.TradingEngine'), \
             patch('aat.strategies.buy_and_hold.BuyAndHoldStrategy'):
            main(['', '--live', '--exchanges=coinbase'])
