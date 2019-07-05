from traitlets import HasTraits, List, Instance, Float, Type, Tuple, Dict, Bool
from .enums import TradingType, ExchangeType, PairType, InstrumentType
from .structs import Instrument


class ExchangeConfig(HasTraits):
    exchange_types = List(trait=Instance(ExchangeType), default_value=[])
    trading_type = Instance(klass=TradingType, args=('NONE',), kwargs={})
    currency_pairs = List(trait=Instance(PairType), default_value=[PairType.BTCUSD])
    instruments = List(trait=Instance(Instrument), default_value=[Instrument(type=InstrumentType.PAIR, underlying=PairType.BTCUSD)])


class SyntheticExchangeConfig(ExchangeConfig):
    exchange_type = Instance(ExchangeType)
    adversaries = List(default_value=[])

    direction = Float(default_value=.5)
    volatility = Float(default_value=200)


class BacktestConfig(HasTraits):
    pass


class RiskConfig(HasTraits):
    max_drawdown = Float(default_value=100.0)  # % Max drawdown before liquidation
    max_risk = Float(default_value=100.0)  # % Max to risk
    total_funds = Float(default_value=0.0)  # total funds available
    trading_type = Instance(klass=TradingType, args=('NONE',), kwargs={})


class ExecutionConfig(HasTraits):
    trading_type = Instance(klass=TradingType, args=('NONE',), kwargs={})


class StrategyConfig(HasTraits):
    clazz = Type()
    args = Tuple(default_value=())
    kwargs = Dict(default_value={})


class TradingEngineConfig(HasTraits):
    type = Instance(klass=TradingType, args=('NONE',), kwargs={})
    print = Bool(default_value=False)
    exchange_options = Instance(klass=ExchangeConfig, args=(), kwargs={})
    backtest_options = Instance(klass=BacktestConfig, args=(), kwargs={})
    risk_options = Instance(klass=RiskConfig, args=(), kwargs={})
    execution_options = Instance(klass=ExecutionConfig, args=(), kwargs={})
    strategy_options = List(trait=Instance(StrategyConfig), default_value=[])  # List of strategy options
