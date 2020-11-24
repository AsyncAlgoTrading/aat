from datetime import datetime
from typing import List, Optional
from .db import InstrumentDB
from ..exchange import ExchangeType
from ...config import InstrumentType, Side
from ...common import _in_cpp
from ...config.enums import OptionType

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
    __brokerId: Optional[str]
    __currency: Optional["Instrument"]
    __underlying: Optional["Instrument"]
    __leg1: Optional["Instrument"]
    __leg2: Optional["Instrument"]
    __leg1_side: Optional[Side]
    __leg2_side: Optional[Side]
    __expiration: Optional[datetime]
    __contract_month: Optional[int]
    __price_increment: Optional[float]
    __unit_value: Optional[float]
    __option_type: Optional[OptionType]

    __slots__ = [
        "__name",
        "__type",
        "__exchanges",
        "__brokerExchange",
        "__brokerId",
        "__currency",
        "__underlying",
        "__leg1",
        "__leg2",
        "__leg1_side",
        "__leg2_side",
        "__expiration",
        "__price_increment",
        "__unit_value",
        "__option_type",
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

    def __init__(
        self,
        name: str,
        type: InstrumentType = InstrumentType.EQUITY,
        exchange: ExchangeType = ExchangeType(""),
        **kwargs,
    ):
        """construct a new instrument instance

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

            brokerId (str): Broker's id  if available
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


        """

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
        if (
            exchange
            and hasattr(self, "_Instrument__exchanges")
            and exchange not in self.__exchanges
        ):
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
        if (
            hasattr(self, "_Instrument__brokerExchange")
            and self.__brokerExchange is not None
        ):
            assert kwargs.get(
                "brokerExchange"
            ) is None or self.__brokerExchange == kwargs.get("brokerExchange")
        else:
            self.__brokerExchange = kwargs.get("brokerExchange")

        if hasattr(self, "_Instrument__brokerId") and self.__brokerId is not None:
            assert kwargs.get("brokerId") is None or self.__brokerId == kwargs.get(
                "brokerId"
            )
        else:
            self.__brokerId = kwargs.get("brokerId")

        if hasattr(self, "_Instrument__currency") and self.__currency is not None:
            assert kwargs.get("currency") is None or self.__currency == kwargs.get(
                "currency"
            )
        else:
            self.__currency = kwargs.get("currency")

        if hasattr(self, "_Instrument__underlying") and self.__underlying is not None:
            assert kwargs.get("underlying") is None or self.__underlying == kwargs.get(
                "underlying"
            )
        else:
            self.__underlying = kwargs.get("underlying")

        if hasattr(self, "_Instrument__leg1") and self.__leg1 is not None:
            assert kwargs.get("leg1") is None or self.__leg1 == kwargs.get("leg1")
        else:
            self.__leg1 = kwargs.get("leg1")

        if hasattr(self, "_Instrument__leg2") and self.__leg2 is not None:
            assert kwargs.get("leg2") is None or self.__leg2 == kwargs.get("leg2")
        else:
            self.__leg2 = kwargs.get("leg2")

        if hasattr(self, "_Instrument__leg1_side") and self.__leg1_side is not None:
            assert kwargs.get("leg1_side") is None or self.__leg1_side == kwargs.get(
                "leg1_side"
            )
        else:
            self.__leg1_side = kwargs.get("leg1_side")

        if hasattr(self, "_Instrument__leg2_side") and self.__leg2_side is not None:
            assert kwargs.get("leg2_side") is None or self.__leg2_side == kwargs.get(
                "leg2_side"
            )
        else:
            self.__leg2_side = kwargs.get("leg2_side")

        if hasattr(self, "_Instrument__expiration"):
            assert kwargs.get("expiration") is None or self.__expiration == kwargs.get(
                "expiration"
            )
        else:
            self.__expiration = kwargs.get("expiration")

        if hasattr(self, "_Instrument__price_increment"):
            assert kwargs.get(
                "price_increment"
            ) is None or self.__price_increment == kwargs.get("price_increment")
        elif kwargs.get("price_increment") is not None:
            self.__price_increment = float(
                kwargs.get("price_increment")  # type: ignore
            )
        else:
            self.__price_increment = None

        if hasattr(self, "_Instrument__unit_value"):
            assert kwargs.get("unit_value") is None or self.__unit_value == kwargs.get(
                "unit_value"
            )
        elif kwargs.get("unit_value") is not None:
            self.__unit_value = float(kwargs.get("unit_value"))  # type: ignore
        else:
            self.__unit_value = None

        if hasattr(self, "_Instrument__option_type"):
            assert kwargs.get(
                "option_type"
            ) is None or self.__option_type == kwargs.get("option_type")
        else:
            self.__option_type = kwargs.get("option_type")

        # Optional Fields Validation
        assert isinstance(self.__brokerExchange, (None.__class__, str))
        assert isinstance(self.__brokerId, (None.__class__, str))
        assert isinstance(self.__currency, (None.__class__, Instrument))
        assert isinstance(self.__underlying, (None.__class__, Instrument))
        assert isinstance(self.__leg1, (None.__class__, Instrument))
        assert isinstance(self.__leg2, (None.__class__, Instrument))
        assert isinstance(self.__leg1_side, (None.__class__, Side))
        assert isinstance(self.__leg2_side, (None.__class__, Side))
        assert isinstance(self.__expiration, (None.__class__, datetime))
        assert isinstance(self.__unit_value, (None.__class__, float))
        assert isinstance(self.__price_increment, (None.__class__, float))
        assert isinstance(self.__option_type, (None.__class__, OptionType))

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
    def brokerId(self):
        return self.__brokerId

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

    @property
    def expiration(self):
        return self.__expiration

    @property
    def unit_value(self):
        return self.__unit_value

    @property
    def price_increment(self):
        return self.__price_increment

    @property
    def option_type(self):
        return self.__option_type

    def __eq__(self, other):
        if other is None:
            return False
        return self.name == other.name and self.type == other.type

    def __hash__(self):
        return hash(str(self))

    def toJson(self):
        return {
            "name": self.name,
            "type": self.type.value,
            "exchanges": [v.toJson() for v in self.exchanges] if self.exchanges else [],
            "brokerExchange": self.brokerExchange,
            "brokerId": self.brokerId,
            "currency": self.currency.toJson() if self.currency else "",
            "underlying": self.underlying.toJson() if self.underlying else "",
            "leg1": self.leg1.toJson() if self.leg1 else "",
            "leg2": self.leg2.toJson() if self.leg2 else "",
            "leg1_side": self.leg1_side.value if self.leg1_side else "",
            "leg2_side": self.leg2_side.value if self.leg2_side else "",
            "expiration": self.expiration.timestamp() if self.expiration else "",
            "price_increment": self.price_increment or "",
            "unit_value": self.unit_value or "",
            "option_type": self.option_type.value if self.option_type else "",
        }

    @staticmethod
    def fromJson(jsn):
        kwargs = {}
        kwargs["name"] = jsn["name"]
        kwargs["type"] = InstrumentType(jsn["type"])
        kwargs["exchanges"] = [ExchangeType.fromJson(e) for e in jsn["exchanges"]]

        if "brokerExchange" in jsn and jsn["brokerExchange"]:
            kwargs["brokerExchange"] = jsn["brokerExchange"]

        if "brokerId" in jsn and jsn["brokerId"]:
            kwargs["brokerId"] = jsn["brokerId"]

        if "currency" in jsn and jsn["currency"]:
            kwargs["currency"] = Instrument.fromJson(jsn["currency"])

        if "underlying" in jsn and jsn["underlying"]:
            kwargs["underlying"] = Instrument.fromJson(jsn["underlying"])

        if "leg1" in jsn and jsn["leg1"]:
            kwargs["leg1"] = Instrument.fromJson(jsn["leg1"])

        if "leg2" in jsn and jsn["leg2"]:
            kwargs["leg2"] = Instrument.fromJson(jsn["leg2"])

        if "leg1_side" in jsn and jsn["leg1_side"]:
            kwargs["leg1_side"] = Side(jsn["leg1_side"])

        if "leg2_side" in jsn and jsn["leg2_side"]:
            kwargs["leg2_side"] = Side(jsn["leg2_side"])

        if "expiration" in jsn and jsn["expiration"]:
            kwargs["expiration"] = datetime.fromtimestamp(jsn["expiration"])

        if "price_increment" in jsn and jsn["price_increment"]:
            kwargs["price_increment"] = jsn["price_increment"]

        if "unit_value" in jsn and jsn["unit_value"]:
            kwargs["unit_value"] = jsn["unit_value"]

        if "option_type" in jsn and jsn["option_type"]:
            kwargs["option_type"] = OptionType(jsn["option_type"])

        return Instrument(**kwargs)

    def __repr__(self):
        return f"Instrument({self.name}-{self.type})"
