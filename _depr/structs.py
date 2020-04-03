from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
from .enums import Side, \
    ExchangeType, \
    ExchangeType_to_string, \
    OptionSide, \
    CurrencyType, \
    PairType, \
    OrderType, \
    OrderSubType, \
    TickType, \
    TickType_to_string, \
    TradeResult, \
    InstrumentType, \
    RiskReason


@dataclass(init=False)
class Struct:
    def to_dict(self, serializable=False, str_timestamp=False, **kwargs) -> dict:
        ret = asdict(self)
        if serializable:
            for item in ret:
                if isinstance(ret[item], datetime):
                    if str_timestamp:
                        ret[item] = ret[item].strftime('%y-%m-%d %H:%M:%S')
                    else:
                        ret[item] = round(ret[item].timestamp())
                elif isinstance(ret[item], Struct) or isinstance(getattr(self, item), Struct):
                    ret[item] = getattr(self, item).to_dict(serializable, str_timestamp, **kwargs)
                elif isinstance(ret[item], Enum) or isinstance(getattr(self, item), Enum):
                    ret[item] = str(getattr(self, item))
                elif isinstance(ret[item], TickType):
                    ret[item] = TickType_to_string(ret[item])
                elif isinstance(ret[item], ExchangeType):
                    ret[item] = ExchangeType_to_string(ret[item])
                elif isinstance(ret[item], float):
                    if ((ret[item] >= float('inf')) is False) and \
                       ((ret[item] <= float('inf')) is False):
                        ret[item] = None
        return ret


@dataclass(init=False)
class Instrument(Struct):
    underlying: PairType
    type: InstrumentType = InstrumentType.PAIR

    def __init__(self,
                 underlying: PairType,
                 type: InstrumentType = InstrumentType.PAIR,
                 *args, **kwargs):
        self.underlying = underlying
        self.type = type

    @property
    def instrument(self):
        return self

    @property
    def currency_pair(self):
        return self.underlying

    def __eq__(self, other):
        return other.currency_pair == self.currency_pair

    def __str__(self):
        return str(self.underlying)

    def __repr__(self):
        return str(self.underlying)

    def __hash__(self):
        return hash(str(self.underlying))


@dataclass(init=False)
class Option(Instrument):
    underlying: Instrument
    expiration: datetime
    strike: float
    size: float
    side: OptionSide

    def __init__(self,
                 underlying: PairType,
                 expiration: datetime,
                 strike: float,
                 size: float,
                 side: OptionSide,
                 type: InstrumentType = InstrumentType.OPTION,
                 *args, **kwargs):
        self.underlying = underlying
        self.expiration = expiration
        self.strike = strike
        self.size = size
        self.side = side
        self.type = type
        super(Option, self).__init__(underlying=underlying,
                                     type=type,
                                     expiration=expiration,
                                     strike=strike,
                                     size=size,
                                     side=side)

    @property
    def instrument(self):
        return self.underlying

    @property
    def currency_pair(self):
        return self.underlying.currency_pair

    def __eq__(self, other):
        return (other.underlying == self.underlying) and \
               (other.currency_pair == self.currency_pair) and \
               (other.expiration == self.expiration) and \
               (other.strike == self.strike) and \
               (other.size == self.size)

    def __str__(self):
        # 180803C00187500-AAPL-CALL
        return self.expiration.strftime('%y%m%d') + \
            self.side.value[:1] + \
            '{0:10.2f}'.format(self.strike).replace(' ', '0') + '-' + \
            str(self.underlying) + '-' + \
            '{0:8.2f}'.format(self.size).replace(' ', '0')


@dataclass(init=False)
class Future(Instrument):
    underlying: Instrument
    expiration: datetime
    size: float

    def __init__(self,
                 underlying: PairType,
                 expiration: datetime,
                 size: float,
                 type: InstrumentType = InstrumentType.FUTURE,
                 *args, **kwargs):
        self.underlying = underlying
        self.expiration = expiration
        self.size = size
        self.type = type
        super(Future, self).__init__(underlying=underlying,
                                     type=type,
                                     expiration=expiration,
                                     size=size)

    @property
    def instrument(self):
        return self.underlying

    @property
    def currency_pair(self):
        return self.underlying.currency_pair

    def __eq__(self, other):
        return (other.underlying == self.underlying) and \
               (other.currency_pair == self.currency_pair) and \
               (other.expiration == self.expiration) and \
               (other.size == self.size)

    def __str__(self):
        # 180803C00187500-AAPL-CALL
        return f'<{self.expiration.strftime("%y%m%d")} - {self.underlying} -  ' + '{0:8.2f}'.format(self.size).replace(' ', '0') + '>'


@dataclass
class MarketData(Struct):
    # common
    time: datetime
    volume: float
    price: float
    type: TickType
    instrument: Instrument
    side: Side

    # maybe specific
    exchange: ExchangeType
    remaining: float = 0.0
    sequence: int = -1
    order_type: OrderType = OrderType.NONE
    order_id: str = ''

    def __eq__(self, other):
        return (self.price == other.price) and \
               (self.instrument == other.instrument) and \
               (self.side == other.side)

    def __str__(self):
        return f'<{self.instrument}-{self.volume}@{self.price}-{self.type}-{self.exchange}-{self.order_id}>'

    def __lt__(self, other):
        return self.price < other.price


@dataclass
class TradeRequest(Struct):
    side: Side
    exchange: ExchangeType

    volume: float
    price: float
    instrument: Instrument

    time: datetime

    order_type: OrderType
    order_sub_type: OrderSubType = OrderSubType.NONE
    risk_check: bool = False
    risk_reason: RiskReason = RiskReason.NONE
    strategy: object = None

    def __str__(self) -> str:
        return f'<{self.instrument}-{self.side}:{self.volume}@{self.price}-{self.order_type}-{self.exchange}>'


@dataclass
class TradeResponse(Struct):
    request: TradeRequest
    side: Side
    exchange: ExchangeType

    volume: float
    price: float
    instrument: Instrument

    time: datetime
    status: TradeResult
    order_id: str

    slippage: float = 0.0
    transaction_cost: float = 0.0
    remaining: float = 0.0
    strategy: object = None

    def __str__(self) -> str:
        return f'<{self.order_id}-{self.instrument}-{self.side}:{self.volume}@{self.price}-{self.status}-{self.exchange}>'


@dataclass
class Account(Struct):
    id: str
    currency: CurrencyType
    balance: float
    exchange: ExchangeType
    value: float
    asOf: datetime

    def __repr__(self) -> str:
        return f'<{self.id} - {self.currency} - {self.balance} - {self.value}>'
