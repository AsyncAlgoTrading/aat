from typing import List
from .db import InstrumentDB
from ..exchange import ExchangeType
from ...config import InstrumentType, Side
from ...common import _in_cpp

try:
    from ...binding import InstrumentCpp  # type: ignore
    _CPP = _in_cpp()
except ImportError:
    _CPP = False


class Instrument(object):
    _instrumentdb = InstrumentDB()
    __exchanges: List[ExchangeType]

    __slots__ = [
        "__name",
        "__type",
        "__exchanges",
        "__brokerExchange",
        "__currency",
        "__underlying",
        "__leg1",
        "__leg2",
        "__leg1_side",
        "__leg2_side",
    ]

    def __new__(cls, *args, **kwargs):
        if cls._instrumentdb.instruments(*args, **kwargs):
            return cls._instrumentdb.get(*args, **kwargs)

        if _CPP:
            # construct with C++
            instrument = InstrumentCpp(*args, **kwargs)
        else:
            # pure python
            instrument = super(Instrument, cls).__new__(cls)

        return instrument

    def __init__(self,
                 name: str,
                 type: InstrumentType = InstrumentType.EQUITY,
                 exchange: ExchangeType = ExchangeType(""),
                 **kwargs):
        '''construct a new instrument instance

        Args:
            name (str): the asset's common name, relative to whatever
                        the exchange's standard is

            type (InstrumentType): the instrument type, dictates the required
                                   extra kwargs

            exchange (ExchangeType): the exchange the instrument can be traded
                                     through
        Kwargs:
            brokerExchange (str): Underlying exchange to use (e.g. not aat.exchange,
                                  but real exchange in cases where aat is wrapping a
                                  broker like IB, TDA, etc)
                Applies to: All

            currency (Instrument): Underlying currency
                Applies to: All

            underlying (Instrument): the underlying asset
                Applies to: OPTION, FUTURE, FUTURESOPTION

            leg1 (Instrument):
                Applies to: PAIR, SPREAD

            leg2 (Instrument):
                Applies to: PAIR, SPREAD

            leg1_side (Side):
                Applies to: SPREAD

            leg2_side (Side):
                Applies to: SPREAD


        '''

        # Validation
        assert isinstance(name, str)
        assert isinstance(type, InstrumentType)
        assert isinstance(exchange, ExchangeType) or not exchange

        # Required fields
        self.__name = name
        self.__type = type

        # FIXME ugly
        if exchange and hasattr(self, "_Instrument__exchanges") and exchange not in self.__exchanges:
            self.__exchanges.append(exchange)
        elif exchange:
            self.__exchanges = [exchange]
        else:
            self.__exchanges = []

        # Optional Fields
        self.__brokerExchange = kwargs.get("brokerExchange")
        self.__currency = kwargs.get("__currency")
        self.__underlying = kwargs.get("__underlying")
        self.__leg1 = kwargs.get("__leg1")
        self.__leg2 = kwargs.get("__leg2")
        self.__leg1_side = kwargs.get("__leg1_side")
        self.__leg2_side = kwargs.get("__leg2_side")

        # Optional Fields Validation
        assert isinstance(self.__brokerExchange, (None.__class__, str))
        assert isinstance(self.__currency, (None.__class__, Instrument))
        assert isinstance(self.__underlying, (None.__class__, Instrument))
        assert isinstance(self.__leg1, (None.__class__, Instrument))
        assert isinstance(self.__leg2, (None.__class__, Instrument))
        assert isinstance(self.__leg1_side, (None.__class__, Side))
        assert isinstance(self.__leg2_side, (None.__class__, Side))

        # install into instrumentdb, noop if already there
        self._instrumentdb.add(self)

    # ******** #
    # Readonly #
    # ******** #
    @property
    def name(self) -> str:
        return self.__name

    @property
    def type(self) -> InstrumentType:
        return self.__type

    @property
    def exchanges(self):
        return self.__exchanges

    def __eq__(self, other):
        return self.name == other.name and self.type == other.type

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        return f'Instrument({self.name}-{self.type})'
