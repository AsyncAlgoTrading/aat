from .utils import config
from .enums import TradingType, ExchangeType, PairType


@config
class ExchangeConfig:
    exchange_types = [ExchangeType], []
    trading_type = TradingType, TradingType.NONE
    currency_pairs = [PairType], [PairType.BTCUSD]


@config
class BacktestConfig:
    pass


@config
class RiskConfig:
    max_drawdown = float, 100.0  # % Max strat drawdown before liquidation
    max_risk = float, 100.0  # % Max to risk on any trade
    total_funds = float, 0.0  # % Of total funds to use
    trading_type = TradingType, TradingType.NONE


@config
class ExecutionConfig:
    trading_type = TradingType, TradingType.NONE


@config
class StrategyConfig:
    clazz = type
    args = tuple, ()
    kwargs = dict, {}


@config
class TradingEngineConfig:
    type = TradingType, TradingType.NONE
    print = bool, False
    exchange_options = ExchangeConfig, ExchangeConfig()
    backtest_options = BacktestConfig, BacktestConfig()
    risk_options = RiskConfig, RiskConfig()
    execution_options = ExecutionConfig, ExecutionConfig()
    strategy_options = [StrategyConfig], []  # List of strategy options
