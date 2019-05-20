# for coverage
from ..config import *
from ..enums import TradingType


class TestConfig:
    def test_ExchangeConfig(self):
        x = ExchangeConfig()
        assert(x.exchange_types == [])
        assert(x.trading_type == TradingType.NONE)

    def test_BacktestConfig(self):
        x = BacktestConfig()
        assert(x)

    def test_RiskConfig(self):
        x = RiskConfig()
        assert(x.max_drawdown == 100.0)
        assert(x.max_risk == 100.0)
        assert(x.total_funds == 0.0)
        assert(x.trading_type == TradingType.NONE)

    def test_ExecutionConfig(self):
        x = ExecutionConfig()
        assert(x.trading_type == TradingType.NONE)

    def test_TradingEngineConfig(self):
        x = TradingEngineConfig()
        assert(x.type == TradingType.NONE)
        assert(x.print is False)
