from datetime import datetime
from typing import Dict, List, Optional, Tuple, Type, Union, cast

from ...config import InstrumentType, Side
from ...config.enums import OptionType
from ..exchange import ExchangeType
from .calendar import TradingDay
from .cpp import _CPP, _make_cpp_instrument
from .db import InstrumentDB


class Instrument(object):
    _instrumentdb = InstrumentDB()

    __exchange: ExchangeType
    __exchanges: List[ExchangeType]
    __type: InstrumentType
    __trading_day: TradingDay
    __broker_exchange: Optional[ExchangeType]
    __broker_id: Optional[str]
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
        "__exchange",
        "__exchanges",
        "__trading_day",
        "__broker_exchange",
        "__broker_id",
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

    def __new__(cls: Type, *args: Tuple, **kwargs: Dict) -> "Instrument":
        if cls._instrumentdb.get(*args, **kwargs):
            return cls._instrumentdb.get(*args, **kwargs)

        if _CPP:
            # construct with C++
            instrument = _make_cpp_instrument(*args, **kwargs)

        else:
            # pure python
            instrument = super(Instrument, cls).__new__(cls)

        return instrument

    def __init__(
        self,
        name: str,
        type: InstrumentType = InstrumentType.EQUITY,
        exchange: ExchangeType = ExchangeType(""),
        **kwargs: Union[
            str,  # key
            "Instrument",  # instrument
            Side,  # side
            ExchangeType,  # exchange
            TradingDay,  # trading calendar
        ],
    ) -> None:
        """construct a new instrument instance

        Args:
            name (str): the asset's common name, relative to whatever
                        the exchange's standard is

            type (InstrumentType): the instrument type, dictates the required
                                   extra kwargs

            exchange (ExchangeType): the exchange the instrument can be traded
                                     through
        Kwargs:
            trading_day (TradingDay): per-exchange trading hours
                Applies to: All

            broker_exchange (str): Underlying exchange to use (e.g. not aat.exchange,
                                  but real exchange in cases where aat is wrapping a
                                  broker like IB, TDA, etc)
                Applies to: All

            broker_id (str): Broker's id  if available
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

            # set attribute
            self.__exchange = exchange

        elif exchange:
            # create new list with this one
            self.__exchanges = [exchange]

            # set attribute
            self.__exchange = exchange

        elif hasattr(self, "_Instrument__exchanges"):
            # do nothing
            pass

        else:
            # no exchange known and no exchange provided
            self.__exchanges = []

            # set attribute
            self.__exchange = exchange

        # Optional Fields
        if hasattr(self, "_Instrument__trading_day") and self.__trading_day is not None:
            assert kwargs.get(
                "trading_day"
            ) is None or self.__trading_day == kwargs.get("trading_day")
        else:
            self.__trading_day: Optional[TradingDay] = cast(
                TradingDay, kwargs.get("trading_day")
            )

        if (
            hasattr(self, "_Instrument__broker_exchange")
            and self.__broker_exchange is not None
        ):
            assert kwargs.get(
                "broker_exchange"
            ) is None or self.__broker_exchange == kwargs.get("broker_exchange")
        else:
            self.__broker_exchange: Optional[ExchangeType] = cast(
                ExchangeType, kwargs.get("broker_exchange")
            )

        if hasattr(self, "_Instrument__broker_id") and self.__broker_id is not None:
            assert kwargs.get("broker_id") is None or self.__broker_id == kwargs.get(
                "broker_id"
            )
        else:
            self.__broker_id: str = cast(str, kwargs.get("broker_id"))

        if hasattr(self, "_Instrument__currency") and self.__currency is not None:
            assert kwargs.get("currency") is None or self.__currency == kwargs.get(
                "currency"
            )
        else:
            self.__currency: "Instrument" = cast("Instrument", kwargs.get("currency"))

        if hasattr(self, "_Instrument__underlying") and self.__underlying is not None:
            assert kwargs.get("underlying") is None or self.__underlying == kwargs.get(
                "underlying"
            )
        else:
            self.__underlying: Optional["Instrument"] = cast(
                "Instrument", kwargs.get("underlying")
            )

        if hasattr(self, "_Instrument__leg1") and self.__leg1 is not None:
            assert kwargs.get("leg1") is None or self.__leg1 == kwargs.get("leg1")
        else:
            self.__leg1: Optional["Instrument"] = cast("Instrument", kwargs.get("leg1"))

        if hasattr(self, "_Instrument__leg2") and self.__leg2 is not None:
            assert kwargs.get("leg2") is None or self.__leg2 == kwargs.get("leg2")
        else:
            self.__leg2: Optional["Instrument"] = cast("Instrument", kwargs.get("leg2"))

        if hasattr(self, "_Instrument__leg1_side") and self.__leg1_side is not None:
            assert kwargs.get("leg1_side") is None or self.__leg1_side == kwargs.get(
                "leg1_side"
            )
        else:
            self.__leg1_side: Optional[Side] = kwargs.get("leg1_side")

        if hasattr(self, "_Instrument__leg2_side") and self.__leg2_side is not None:
            assert kwargs.get("leg2_side") is None or self.__leg2_side == kwargs.get(
                "leg2_side"
            )
        else:
            self.__leg2_side: Optional[Side] = kwargs.get("leg2_side")

        if hasattr(self, "_Instrument__expiration"):
            assert kwargs.get("expiration") is None or self.__expiration == kwargs.get(
                "expiration"
            )
        else:
            self.__expiration: datetime = cast(datetime, kwargs.get("expiration"))

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
            self.__option_type: OptionType = cast(OptionType, kwargs.get("option_type"))

        # Optional Fields Validation
        assert isinstance(self.__broker_exchange, (None.__class__, str))
        assert isinstance(self.__broker_id, (None.__class__, str))
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
    def exchanges(self) -> List[ExchangeType]:
        return self.__exchanges

    @property
    def exchange(self) -> ExchangeType:
        return self.__exchange

    def tradingLines(
        self, exchange: Optional[ExchangeType] = None
    ) -> List["Instrument"]:
        """Returns other exchanges that the same instrument trades on

        Returns:
            exchange (ExchangeType): Exchange to filter by
        """
        return self._instrumentdb.instruments(self.name, self.type, exchange)

    def synthetics(
        self,
        type: Optional[InstrumentType] = None,
        exchange: Optional[ExchangeType] = None,
    ) -> List["Instrument"]:
        """Returns other instruments with the same name

        Returns:
            type (InstrumentType): instrument type to filter by, e.g. for an equity, filter to only get ADRs
            exchange (ExchangeType): Exchange to filter by
        """
        return self._instrumentdb.instruments(self.name, type, exchange)

    # ******** #
    # Optional #
    # ******** #
    @property
    def tradingDay(self) -> TradingDay:
        return self.__trading_day

    @property
    def brokerExchange(self) -> Optional[ExchangeType]:
        return self.__broker_exchange

    @property
    def brokerId(self) -> Optional[str]:
        return self.__broker_id

    @property
    def currency(self) -> Optional["Instrument"]:
        return self.__currency

    @property
    def underlying(self) -> Optional["Instrument"]:
        return self.__underlying

    @property
    def leg1(self) -> Optional["Instrument"]:
        return self.__leg1

    @property
    def leg2(self) -> Optional["Instrument"]:
        return self.__leg2

    @property
    def leg1Side(self) -> Optional[Side]:
        return self.__leg1_side

    @property
    def leg2Side(self) -> Optional[Side]:
        return self.__leg2_side

    @property
    def expiration(self) -> Optional[datetime]:
        return self.__expiration

    @property
    def unitValue(self) -> Optional[float]:
        return self.__unit_value

    @property
    def priceIncrement(self) -> Optional[float]:
        return self.__price_increment

    @property
    def optionType(self) -> Optional[OptionType]:
        return self.__option_type

    def __eq__(self, other: object) -> bool:
        if other is None:
            return False
        if not isinstance(other, Instrument):
            raise TypeError()
        return self.name == other.name and self.type == other.type

    def __hash__(self) -> int:
        return hash(str(self))

    def json(self) -> dict:
        return {
            "name": self.name,
            "type": self.type.value,
            "exchanges": [v.json() for v in self.exchanges] if self.exchanges else [],
            "broker_exchange": self.brokerExchange,
            "broker_id": self.brokerId,
            "currency": self.currency.json() if self.currency else "",
            "underlying": self.underlying.json() if self.underlying else "",
            "leg1": self.leg1.json() if self.leg1 else "",
            "leg2": self.leg2.json() if self.leg2 else "",
            "leg1_side": self.leg1Side.value if self.leg1Side else "",
            "leg2_side": self.leg2Side.value if self.leg2Side else "",
            "expiration": self.expiration.timestamp() if self.expiration else "",
            "price_increment": self.priceIncrement or "",
            "unit_value": self.unitValue or "",
            "option_type": self.optionType.value if self.optionType else "",
        }

    @staticmethod
    def fromJson(jsn: dict) -> "Instrument":
        kwargs = {}
        kwargs["name"] = jsn["name"]
        kwargs["type"] = InstrumentType(jsn["type"])
        kwargs["exchanges"] = [ExchangeType.fromJson(e) for e in jsn["exchanges"]]

        if "broker_exchange" in jsn and jsn["broker_exchange"]:
            kwargs["broker_exchange"] = jsn["broker_exchange"]

        if "broker_id" in jsn and jsn["broker_id"]:
            kwargs["broker_id"] = jsn["broker_id"]

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

    def __repr__(self) -> str:
        return f"Instrument({self.name}-{self.type})"
