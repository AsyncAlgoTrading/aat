from enum import Enum
from ..binding import Side, InstrumentType, EventType, DataType  # noqa: F401


class BaseEnum(Enum):
    @classmethod
    def members(cls):
        return cls.__members__.keys()

    @classmethod
    def keys(cls):
        return cls.__members__.values()

    def __str__(self):
        return f'{self.value}'


class OrderType(BaseEnum):
    # Order Types
    LIMIT = 'LIMIT'
    MARKET = 'MARKET'
    STOP_MARKET = 'STOP_MARKET'
    STOP_LIMIT = 'STOP_LIMIT'


class OrderFlag(BaseEnum):
    # Order flags
    NONE = 'NONE'  # normal order
    FILL_OR_KILL = 'FILL_OR_KILL'  # fill entire order or cancel
    ALL_OR_NONE = 'ALL_OR_NONE'  # fill entire order in single transaction or cancel
    IMMEDIATE_OR_CANCEL = 'IMMEDIATE_OR_CANCEL'  # fill what you can immediately, cancel the rest
