from enum import Enum


class BaseEnum(Enum):
    @classmethod
    def members(cls):
        return cls.__members__.keys()

    def __str__(self):
        return f'{self.value}'

class InstrumentType(BaseEnum):
    CURRENCY = 'CURRENCY'
    # PAIR = 'PAIR'
    EQUITY = 'EQUITY'
    # BOND = 'BOND'
    # OPTION = 'OPTION'
    # FUTURE = 'FUTURE'
