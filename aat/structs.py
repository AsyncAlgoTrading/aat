import datetime
from .enums import Side, \
                   ExchangeType, \
                   OptionSide, \
                   CurrencyType, \
                   PairType, \
                   OrderType, \
                   OrderSubType, \
                   TickType, \
                   TradeResult, \
                   InstrumentType, \
                   RiskReason, \
                   ChangeReason
from .utils import struct, NOPRINT


@struct
class Instrument:
    type = InstrumentType, InstrumentType.PAIR
    underlying = PairType

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

    def __hash__(self):
        return hash(str(self.underlying))


@struct
class Option(Instrument):
    type = InstrumentType, InstrumentType.OPTION
    underlying = Instrument
    expiration = datetime.datetime
    strike = float
    size = float
    side = OptionSide

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


@struct
class Future(Instrument):
    type = InstrumentType, InstrumentType.FUTURE
    underlying = Instrument
    expiration = datetime.datetime
    size = float

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
        return self.expiration.strftime('%y%m%d') + '-' + str(self.underlying) + '-' + '{0:8.2f}'.format(self.size).replace(' ', '0')


@struct
class MarketData:
    # common
    time = datetime.datetime, NOPRINT
    volume = float
    price = float
    type = TickType
    instrument = Instrument
    side = Side

    # maybe specific
    remaining = float, 0.0
    reason = ChangeReason, ChangeReason.NONE
    sequence = int, -1
    exchange = ExchangeType
    order_type = OrderType, OrderType.NONE

    def __eq__(self, other):
        return (self.price == other.price) and \
               (self.instrument == other.instrument) and \
               (self.side == other.side)

    def __lt__(self, other):
        return self.price < other.price


@struct
class TradeRequest:
    side = Side

    volume = float
    price = float
    instrument = Instrument

    order_type = OrderType
    order_sub_type = OrderSubType, OrderSubType.NONE
    # exchange = ExchangeType

    time = datetime.datetime, datetime.datetime.now()  # FIXME
    risk_check = bool, False
    risk_reason = RiskReason, RiskReason.NONE


@struct
class TradeResponse:
    request = TradeRequest
    side = Side

    volume = float
    price = float
    instrument = Instrument

    slippage = float, 0.0
    transaction_cost = float, 0.0

    time = datetime.datetime, datetime.datetime.now()  # FIXME
    status = TradeResult
    order_id = str
    remaining = float, 0.0


@struct
class Account:
    id = str
    currency = CurrencyType
    balance = float
    exchange = ExchangeType

    def __repr__(self) -> str:
        return "<" + self.id + " - " + str(self.currency) + " - " + str(self.balance) + ">"
