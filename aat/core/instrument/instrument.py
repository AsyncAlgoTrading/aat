from typing import List, Optional
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
    __type: InstrumentType
    __brokerExchange: Optional[str]
    __currency: Optional['Instrument']
    __underlying: Optional['Instrument']
    __leg1: Optional['Instrument']
    __leg2: Optional['Instrument']
    __leg1_side: Optional[Side]
    __leg2_side: Optional[Side]

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
        self.__name = name  # noop if already exists

        if hasattr(self, "_Instrument__type"):
            assert self.__type == type
        else:
            self.__type = type

        # FIXME ugly
        if exchange and hasattr(self, "_Instrument__exchanges") and exchange not in self.__exchanges:
            # append this exchange to list of available
            self.__exchanges.append(exchange)
        elif exchange:
            # create new list with this one
            self.__exchanges = [exchange]
        elif hasattr(self, "_Instrument__exchanges"):
            # do nothing
            pass
        else:
            # no exchange known and no exchange provided
            self.__exchanges = []

        # Optional Fields
        if hasattr(self, "_Instrument__brokerExchange"):
            assert kwargs.get('brokerExchange') is None or self.__brokerExchange == kwargs.get("brokerExchange")
        else:
            self.__brokerExchange = kwargs.get("brokerExchange")

        if hasattr(self, "_Instrument__currency"):
            assert kwargs.get('currency') is None or self.__currency == kwargs.get("currency")
        else:
            self.__currency = kwargs.get("currency")

        if hasattr(self, "_Instrument__underlying"):
            assert kwargs.get('underlying') is None or self.__underlying == kwargs.get("underlying")
        else:
            self.__underlying = kwargs.get("underlying")

        if hasattr(self, "_Instrument__leg1"):
            assert kwargs.get('leg1') is None or self.__leg1 == kwargs.get("leg1")
        else:
            self.__leg1 = kwargs.get("leg1")

        if hasattr(self, "_Instrument__leg2"):
            assert kwargs.get('leg2') is None or self.__leg2 == kwargs.get("leg2")
        else:
            self.__leg2 = kwargs.get("leg2")

        if hasattr(self, "_Instrument__leg1_side"):
            assert kwargs.get('leg1_side') is None or self.__leg1_side == kwargs.get("leg1_side")
        else:
            self.__leg1_side = kwargs.get("leg1_side")

        if hasattr(self, "_Instrument__leg2_side"):
            assert kwargs.get('leg2_side') is None or self.__leg2_side == kwargs.get("leg2_side")
        else:
            self.__leg2_side = kwargs.get("leg2_side")

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

    # ******** #
    # Optional #
    # ******** #
    @property
    def brokerExchange(self):
        return self.__brokerExchange

    @property
    def currency(self):
        return self.__currency

    @property
    def underlying(self):
        return self.__underlying

    @property
    def leg1(self):
        return self.__leg1

    @property
    def leg2(self):
        return self.__leg2

    @property
    def leg1_side(self):
        return self.__leg1_side

    @property
    def leg2_side(self):
        return self.__leg2_side

    def __eq__(self, other):
        return self.name == other.name and self.type == other.type

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        return f'Instrument({self.name}-{self.type})'
