from enum import Enum
# from ._enums import EventType, DataType


class BaseEnum(Enum):
    @classmethod
    def members(cls):
        return cls.__members__.keys()

    @classmethod
    def keys(cls):
        return cls.__members__.values()

    def __str__(self):
        return f'{self.value}'


class InstrumentType(BaseEnum):
    CURRENCY = 'CURRENCY'
    # PAIR = 'PAIR'
    EQUITY = 'EQUITY'
    # BOND = 'BOND'
    # OPTION = 'OPTION'
    # FUTURE = 'FUTURE'


class Side(BaseEnum):
    BUY = 'BUY'
    SELL = 'SELL'


class EventType(BaseEnum):
    # Trade events
    TRADE = 'TRADE'

    # Order events
    OPEN = 'OPEN'
    CANCEL = 'CANCEL'
    CHANGE = 'CHANGE'
    FILL = 'FILL'

    # Other data events
    DATA = 'DATA'

    # System events
    HALT = 'HALT'
    CONTINUE = 'CONTINUE'

    # Engine events
    ERROR = 'ERROR'
    START = 'START'
    EXIT = 'EXIT'


class DataType(BaseEnum):
    ORDER = 'ORDER'
    TRADE = 'TRADE'
