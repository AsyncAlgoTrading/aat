from datetime import datetime
from typing import Tuple, Union, Dict, Type, List

from aat.core.exchange import ExchangeType
from aat.core.instrument import Instrument
from aat.common import _merge

from .cpp import _CPP, _make_cpp_cash


class CashPosition(object):
    __slots__ = ["__notional", "__notional_history", "__instrument", "__exchange"]

    def __new__(cls: Type, *args: Tuple, **kwargs: Dict) -> "CashPosition":
        if _CPP:
            return _make_cpp_cash(*args, **kwargs)
        return super(CashPosition, cls).__new__(cls)

    def __init__(
        self,
        notional: float,
        timestamp: datetime,
        instrument: Instrument,
        exchange: ExchangeType,
    ) -> None:
        assert instrument is None or isinstance(instrument, Instrument)
        assert isinstance(exchange, ExchangeType)

        self.__instrument = instrument
        self.__exchange = exchange

        assert isinstance(notional, (int, float))

        self.__notional = notional
        self.__notional_history = [(notional, timestamp)]

    # ******** #
    # Readonly #
    # ******** #
    @property
    def instrument(self) -> Instrument:
        return self.__instrument

    @property
    def exchange(self) -> ExchangeType:
        return self.__exchange

    @property
    def timestamp(self) -> datetime:
        """time of creation of initial position"""
        return self.__notional_history[0][1]

    @property
    def notionalHistory(self) -> List[Tuple[float, datetime]]:
        return self.__notional_history

    # ***********#
    # Read/write #
    # ***********#
    @property
    def notional(self) -> float:
        return self.__notional

    @notional.setter
    def notional(
        self, notional: Union[Tuple[Union[int, float], datetime], Union[int, float]]
    ) -> None:
        """Tuple as we need temporal information for history"""
        assert isinstance(notional, tuple)
        notional, when = notional

        assert isinstance(notional, (int, float))
        assert isinstance(when, datetime)

        self.__notional = notional
        self.__notional_history.append((self.notional, when))

    def json(self) -> dict:
        return {
            "timestamp": self.timestamp.timestamp(),
            "instrument": self.instrument.json(),
            "exchange": self.exchange.json(),
            "notional": self.notional,
            "notional_history": self.notionalHistory,
        }

    @staticmethod
    def fromJson(jsn: dict) -> "CashPosition":
        kwargs = {}
        kwargs["notional"] = jsn["notional"]
        kwargs["timestamp"] = datetime.fromtimestamp(jsn["timestamp"])
        kwargs["instrument"] = Instrument.fromJson(jsn["instrument"])
        kwargs["exchange"] = ExchangeType.fromJson(jsn["exchange"])

        ret = CashPosition(**kwargs)
        ret.__notional_history = [
            (x, datetime.fromtimestamp(y)) for x, y in jsn["notional_history"]
        ]
        return ret

    def __repr__(self) -> str:
        return f"Cash(notional={self.notional}, instrument={self.instrument}, exchange={self.exchange})"

    def __add__(self, other: object) -> "CashPosition":
        """Adding positions should give you the net position"""
        assert isinstance(other, CashPosition)
        assert self.instrument == other.instrument

        # collect histories
        notional_history = _merge(self.__notional_history, other.__notional_history)

        ret = CashPosition(
            notional_history[-1][0],
            self.timestamp,
            self.instrument,
            self.exchange,  # FIXME
        )

        ret.__notional_history = notional_history
        return ret
