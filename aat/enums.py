from functools import lru_cache
from enum import Enum
from ._enums import (  # noqa: F401
    TickType,
    TickTypes,
    TickType_to_string,
    TickType_from_string,
    ExchangeType,
    ExchangeTypes,
    ExchangeType_to_string,
    ExchangeType_from_string,
    )


class BaseEnum(Enum):
    @classmethod
    def members(cls):
        return cls.__members__.keys()


class TradingType(BaseEnum):
    NONE = 'NONE'
    SANDBOX = 'SANDBOX'
    LIVE = 'LIVE'
    BACKTEST = 'BACKTEST'
    SIMULATION = 'SIMULATION'


class CurrencyType(BaseEnum):
    NONE = 'NONE'  # special, dont use

    USD = 'USD'
    EUR = 'EUR'
    GBP = 'GBP'

    USDC = 'USDC'
    USDT = 'USDT'

    BAT = 'BAT'
    BCH = 'BCH'
    BTC = 'BTC'
    CVC = 'CVC'
    DAI = 'DAI'
    DNT = 'DNT'
    EOS = 'EOS'
    ETC = 'ETC'
    ETH = 'ETH'
    GNT = 'GNT'
    LINK = 'LINK'
    LOOM = 'LOOM'
    LTC = 'LTC'
    MANA = 'MANA'
    REP = 'REP'
    XLM = 'XLM'
    XRP = 'XRP'
    ZEC = 'ZEC'
    ZRX = 'ZRX'


def _joiner(l):
    for i, a in enumerate(l):
        for j, b in enumerate(l):
            if i != j and i != CurrencyType.NONE and j != CurrencyType.NONE:
                yield (a, b)
    yield (CurrencyType.NONE, CurrencyType.NONE)


class _PairType(BaseEnum):
    def __str__(self):
        return str(self.value[0].value) + '/' + str(self.value[1].value)

    def __hash__(self):
        return hash(str(self))

    @staticmethod
    @lru_cache(None)
    def from_string(first, second=''):
        if second:
            c1 = CurrencyType(first)
            c2 = CurrencyType(second)
            return PairType((c1, c2))
        first = first.strip().upper().replace('-', '/')
        if '/' not in first:
            for i in range(len(first)):
                if i == 0:
                    continue
                try:
                    c1 = CurrencyType(first[:i])
                    c2 = CurrencyType(first[i:])
                    return PairType.from_string(c1, c2)
                except ValueError:
                    continue
        first, second = first.split('/')
        c1 = CurrencyType(first)
        c2 = CurrencyType(second)
        return PairType((c1, c2))


PairType = _PairType('PairType', {(x[0].value + x[1].value if x[0] != CurrencyType.NONE else x[0].value): (x[0], x[1]) for x in _joiner(CurrencyType.__members__.values())})


class Side(BaseEnum):
    NONE = 'NONE'
    BUY = 'BUY'
    SELL = 'SELL'


class OptionSide(BaseEnum):
    NONE = 'NONE'
    CALL = 'CALL'
    PUT = 'PUT'


class OrderType(BaseEnum):
    NONE = 'NONE'
    MARKET = 'MARKET'
    LIMIT = 'LIMIT'


class OrderSubType(BaseEnum):
    NONE = 'NONE'
    POST_ONLY = 'POST_ONLY'
    FILL_OR_KILL = 'FILL_OR_KILL'
    # ALL_OR_NOTHING = 3


class TradeResult(BaseEnum):
    NONE = 'NONE'
    PENDING = 'PENDING'
    PARTIAL = 'PARTIAL'
    FILLED = 'FILLED'
    REJECTED = 'REJECTED'


class InstrumentType(BaseEnum):
    COIN = 'COIN'
    PAIR = 'PAIR'
    OPTION = 'OPTION'
    FUTURE = 'FUTURE'


class RiskReason(BaseEnum):
    NONE = 'NONE'
    PARTIAL = 'PARTIAL'
    FULL = 'FULL'
