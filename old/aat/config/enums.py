from typing import List
from enum import Enum


class BaseEnum(Enum):
    def __str__(self) -> str:
        return f"{self.value}"

    @classmethod
    def members(cls) -> List[str]:
        return list(cls.__members__.keys())


class TradingType(BaseEnum):
    LIVE = "LIVE"
    SIMULATION = "SIMULATION"
    SANDBOX = "SANDBOX"
    BACKTEST = "BACKTEST"


class Side(BaseEnum):
    BUY = "BUY"
    SELL = "SELL"


class OptionType(BaseEnum):
    CALL = "CALL"
    PUT = "PUT"


class EventType(BaseEnum):
    # Heartbeat events
    HEARTBEAT = "HEARTBEAT"

    # Trade events
    TRADE = "TRADE"

    # Order events
    OPEN = "OPEN"
    CANCEL = "CANCEL"
    CHANGE = "CHANGE"
    FILL = "FILL"

    # Other data events
    DATA = "DATA"

    # System events
    HALT = "HALT"
    CONTINUE = "CONTINUE"

    # Engine events
    ERROR = "ERROR"
    START = "START"
    EXIT = "EXIT"

    # Order Events
    BOUGHT = "BOUGHT"
    SOLD = "SOLD"
    RECEIVED = "RECEIVED"
    REJECTED = "REJECTED"
    CANCELED = "CANCELED"


class DataType(BaseEnum):
    DATA = "DATA"
    ERROR = "ERROR"

    ORDER = "ORDER"
    TRADE = "TRADE"


class InstrumentType(BaseEnum):
    OTHER = "OTHER"

    EQUITY = "EQUITY"

    # TODO ETF separate?

    BOND = "BOND"

    OPTION = "OPTION"

    FUTURE = "FUTURE"

    PAIR = "PAIR"

    SPREAD = "SPREAD"

    FUTURESOPTION = "FUTURESOPTION"

    MUTUALFUND = "MUTUALFUND"

    COMMODITY = "COMMODITY"

    # TODO Warrant?

    # Non-tradeable
    CURRENCY = "CURRENCY"
    INDEX = "INDEX"


class OrderType(BaseEnum):
    # Order Types
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP = "STOP"


class OrderFlag(BaseEnum):
    # Order Flag
    NONE = "NONE"
    FILL_OR_KILL = "FILL_OR_KILL"
    ALL_OR_NONE = "ALL_OR_NONE"
    IMMEDIATE_OR_CANCEL = "IMMEDIATE_OR_CANCEL"


class ExitRoutine(BaseEnum):
    NONE = "NONE"
    CLOSE_ALL = "CLOSE_ALL"
