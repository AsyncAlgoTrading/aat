from enum import Enum


class BaseEnum(Enum):
    def __str__(self):
        return f'{self.value}'

 
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


class InstrumentType(BaseEnum):		
    CURRENCY = 'CURRENCY'		
    # PAIR = 'PAIR'		
    EQUITY = 'EQUITY'		
    # BOND = 'BOND'		
    # OPTION = 'OPTION'		
    # FUTURE = 'FUTURE'		

 
class OrderType(BaseEnum):
    # Order Types
    LIMIT = 'LIMIT'
    MARKET = 'MARKET'
    STOP = 'STOP'

class OrderFlag(BaseEnum):
    # Order Flag
    NONE = 'NONE'
    FILL_OR_KILL = 'FILL_OR_KILL'
    ALL_OR_NONE = 'ALL_OR_NONE'
    IMMEDIATE_OR_CANCEL = 'IMMEDIATE_OR_CANCEL'
