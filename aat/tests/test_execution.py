from mock import patch, MagicMock
from datetime import datetime


class TestExecution:
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
        from ..execution import Execution
        from ..config import ExecutionConfig

        ex = MagicMock()

        ec = ExecutionConfig()
        e = Execution(ec, ex)
        assert e

    def test_request(self):
        from ..execution import Execution
        from ..enums import Side, PairType, OrderType
        from ..config import ExecutionConfig
        from ..structs import TradeRequest, Instrument

        ex = MagicMock()
        ec = ExecutionConfig()
        e = Execution(ec, ex)

        req = TradeRequest(side=Side.BUY,
                           instrument=Instrument(underlying=PairType.BTCUSD),
                           order_type=OrderType.MARKET,
                           volume=1.0,
                           price=1.0)

        resp = e.request(req)

        req = TradeRequest(side=Side.SELL,
                           instrument=Instrument(underlying=PairType.BTCUSD),
                           order_type=OrderType.MARKET,
                           volume=1.0,
                           price=1.0)

        resp = e.request(req)

        req = TradeRequest(side=Side.BUY,
                           instrument=Instrument(underlying=PairType.BTCUSD),
                           order_type=OrderType.MARKET,
                           volume=1.0,
                           price=1.0)

        resp = e.request(req)

        e.cancel(resp)
        e.cancelAll()
