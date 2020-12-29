from datetime import datetime
from typing import Tuple, Union, Mapping, Type, Dict, List

from aat.core.data import Trade
from aat.core.exchange import ExchangeType
from aat.core.instrument import Instrument
from aat.common import _merge

from .cpp import _CPP, _make_cpp_position


class Position(object):
    __slots__ = [
        "__size",
        "__size_history",
        "__notional",
        "__notional_history",
        "__price",
        "__price_history",
        "__investment",
        "__investment_history",
        "__instrumentPrice",
        "__instrumentPrice_history",
        "__instrument",
        "__exchange",
        "__pnl",
        "__pnl_history",
        "__unrealizedPnl",
        "__unrealizedPnl_history",
        "__trades",
    ]

    def __new__(cls: Type, *args: Tuple, **kwargs: Dict) -> "Position":
        if _CPP:
            return _make_cpp_position(*args, **kwargs)
        return super(Position, cls).__new__(cls)

    def __init__(
        self,
        size: float,
        price: float,
        timestamp: datetime,
        instrument: Instrument,
        exchange: ExchangeType,
        trades: List[Trade],
    ) -> None:
        assert instrument is None or isinstance(instrument, Instrument)
        assert isinstance(exchange, ExchangeType)

        self.__instrument = instrument
        self.__exchange = exchange

        assert isinstance(size, (int, float))
        assert isinstance(price, (int, float))

        self.__size = size
        self.__size_history = [(size, timestamp)]

        self.__price = price
        self.__price_history = [(price, timestamp)]

        self.__investment = size * price
        self.__investment_history = [(self.__investment, timestamp)]

        self.__notional = self.__investment
        self.__notional_history = [(self.__investment, timestamp)]
        self.__instrumentPrice = price
        self.__instrumentPrice_history = [(price, timestamp)]

        self.__pnl = 0.0
        self.__pnl_history = [(0.0, timestamp)]

        self.__unrealizedPnl = 0.0
        self.__unrealizedPnl_history = [(0.0, timestamp)]

        self.__trades = trades

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
        return self.__size_history[0][1]

    @property
    def sizeHistory(self) -> List[Tuple[float, datetime]]:
        return self.__size_history

    @property
    def priceHistory(self) -> List[Tuple[float, datetime]]:
        return self.__price_history

    @property
    def investmentHistory(self) -> List[Tuple[float, datetime]]:
        return self.__investment_history

    @property
    def notionalHistory(self) -> List[Tuple[float, datetime]]:
        return self.__notional_history

    @property
    def instrumentPriceHistory(self) -> List[Tuple[float, datetime]]:
        return self.__instrumentPrice_history

    @property
    def pnlHistory(self) -> List[Tuple[float, datetime]]:
        return self.__pnl_history

    @property
    def unrealizedPnlHistory(self) -> List[Tuple[float, datetime]]:
        return self.__unrealizedPnl_history

    # ***********#
    # Read/write #
    # ***********#
    @property
    def instrumentPrice(self) -> float:
        return round(self.__instrumentPrice, 4)

    @instrumentPrice.setter
    def instrumentPrice(
        self,
        instrument_price: Union[Tuple[Union[int, float], datetime], Union[int, float]],
    ) -> None:
        """Tuple as we need temporal information for history"""
        assert isinstance(instrument_price, tuple)
        instrument_price, when = instrument_price

        assert isinstance(instrument_price, (int, float))
        assert isinstance(when, datetime)

        self.__instrumentPrice = instrument_price
        self.__instrumentPrice_history.append((self.instrumentPrice, when))

        if self.size != 0:
            self.__notional_history.append((self.size * self.instrumentPrice, when))

    @property
    def size(self) -> float:
        return self.__size

    @size.setter
    def size(
        self, size: Union[Tuple[Union[int, float], datetime], Union[int, float]]
    ) -> None:
        """Tuple as we need temporal information for history"""
        assert isinstance(size, tuple)
        size, when = size

        assert isinstance(size, (int, float))
        assert isinstance(when, datetime)

        self.__size = size
        self.__size_history.append((self.size, when))

    @property
    def price(self) -> float:
        return round(self.__price, 4)

    @price.setter
    def price(
        self, price: Union[Tuple[Union[int, float], datetime], Union[int, float]]
    ) -> None:
        """Tuple as we need temporal information for history"""
        assert isinstance(price, tuple)
        price, when = price

        assert isinstance(price, (int, float))
        assert isinstance(when, datetime)

        self.__price = price
        self.__price_history.append((self.price, when))
        self.investment = (self.size * self.price, when)  # type: ignore # TODO why is this one being flagged

    @property
    def investment(self) -> float:
        return round(self.__investment, 4)

    @investment.setter
    def investment(
        self, investment: Union[Tuple[Union[int, float], datetime], Union[int, float]]
    ) -> None:
        """Tuple as we need temporal information for history"""
        assert isinstance(investment, tuple)
        investment, when = investment

        assert isinstance(investment, (int, float))
        assert isinstance(when, datetime)

        self.__investment = investment
        self.__investment_history.append((self.investment, when))

    @property
    def notional(self) -> float:
        return round(self.__notional, 4)

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

    @property
    def pnl(self) -> float:
        return round(self.__pnl, 4)

    @pnl.setter
    def pnl(
        self, pnl: Union[Tuple[Union[int, float], datetime], Union[int, float]]
    ) -> None:
        """Tuple as we need temporal information for history"""
        assert isinstance(pnl, tuple)
        pnl, when = pnl

        assert isinstance(pnl, (int, float))
        assert isinstance(when, datetime)

        self.__pnl = pnl
        self.__pnl_history.append((self.pnl, when))

    @property
    def unrealizedPnl(self) -> float:
        return round(self.__unrealizedPnl, 4)

    @unrealizedPnl.setter
    def unrealizedPnl(
        self,
        unrealized_pnl: Union[Tuple[Union[int, float], datetime], Union[int, float]],
    ) -> None:
        """Tuple as we need temporal information for history"""
        assert isinstance(unrealized_pnl, tuple)
        unrealized_pnl, when = unrealized_pnl

        assert isinstance(unrealized_pnl, (int, float))
        assert isinstance(when, datetime)

        self.__unrealizedPnl = unrealized_pnl
        self.__unrealizedPnl_history.append((self.unrealizedPnl, when))

    @property
    def trades(self) -> List[Trade]:
        return self.__trades

    def json(self) -> dict:
        return {
            "timestamp": self.timestamp.timestamp(),
            "instrument": self.instrument.json(),
            "exchange": self.exchange.json(),
            "size": self.size,
            "size_history": self.sizeHistory,
            "notional": self.notional,
            "notional_history": self.notionalHistory,
            "price": self.price,
            "price_history": self.priceHistory,
            "investment": self.investment,
            "investment_history": self.investmentHistory,
            "instrumentPrice": self.instrumentPrice,
            "instrumentPrice_history": self.instrumentPriceHistory,
            "pnl": self.pnl,
            "pnl_history": self.pnlHistory,
            "unrealizedPnl": self.unrealizedPnl,
            "unrealizedPnl_history": self.unrealizedPnlHistory,
            "trades": [t.json() for t in self.trades],
        }

    @staticmethod
    def fromJson(jsn: dict) -> "Position":
        kwargs = {}
        kwargs["size"] = jsn["size"]
        kwargs["price"] = jsn["price"]
        kwargs["timestamp"] = datetime.fromtimestamp(jsn["timestamp"])
        kwargs["instrument"] = Instrument.fromJson(jsn["instrument"])
        kwargs["exchange"] = ExchangeType.fromJson(jsn["exchange"])
        kwargs["trades"] = [Trade.fromJson(x) for x in jsn["trades"]]

        ret = Position(**kwargs)
        ret.__notional = jsn["notional"]
        ret.__investment = jsn["investment"]
        ret.__instrumentPrice = jsn["instrumentPrice"]
        ret.__pnl = jsn["pnl"]
        ret.__unrealizedPnl = jsn["unrealizedPnl"]

        ret.__size_history = [
            (x, datetime.fromtimestamp(y)) for x, y in jsn["size_history"]
        ]
        ret.__notional_history = [
            (x, datetime.fromtimestamp(y)) for x, y in jsn["notional_history"]
        ]
        ret.__price_history = [
            (x, datetime.fromtimestamp(y)) for x, y in jsn["price_history"]
        ]
        ret.__investment_history = [
            (x, datetime.fromtimestamp(y)) for x, y in jsn["investment_history"]
        ]
        ret.__instrumentPrice_history = [
            (x, datetime.fromtimestamp(y)) for x, y in jsn["instrumentPrice_history"]
        ]
        ret.__pnl_history = [
            (x, datetime.fromtimestamp(y)) for x, y in jsn["pnl_history"]
        ]
        ret.__unrealizedPnl_history = [
            (x, datetime.fromtimestamp(y)) for x, y in jsn["unrealizedPnl_history"]
        ]
        return ret

    @staticmethod
    def schema() -> Mapping[str, Type]:
        return {
            "timestamp": int,
            "instrument": str,
            "exchange": str,
            "size": float,
            "notional": float,
            "price": float,
            "investment": float,
            "instrumentPrice": float,
            "pnl": float,
            "unrealizedPnl": float,
        }

    def __repr__(self) -> str:
        return f"Position(price={self.price}, size={self.size}, notional={self.notional}, pnl={self.pnl}, unrealizedPnl={self.unrealizedPnl}, instrument={self.instrument}, exchange={self.exchange})"

    def __add__(self, other: object) -> "Position":
        """Adding positions should give you the net position"""
        assert isinstance(other, Position)
        assert self.instrument == other.instrument

        # collect histories
        size_history = _merge(self.__size_history, other.__size_history)
        notional_history = _merge(self.__notional_history, other.__notional_history)
        price_history = _merge(self.__price_history, other.__price_history, False)
        investment_history = _merge(
            self.__investment_history, other.__investment_history
        )
        instrumentPrice_history = _merge(
            self.__instrumentPrice_history, other.__instrumentPrice_history, False
        )
        pnl_history = _merge(self.__pnl_history, other.__pnl_history)
        unrealizedPnl_history = _merge(
            self.__unrealizedPnl_history, other.__unrealizedPnl_history
        )

        ret = Position(
            size_history[-1][0],
            price_history[-1][0],
            size_history[-1][1],
            self.instrument,
            self.exchange,  # FIXME
            self.trades + other.trades,
        )

        ret.__size_history = size_history
        ret.__notional_history = notional_history
        ret.__price_history = price_history
        ret.__investment_history = investment_history
        ret.__instrumentPrice_history = instrumentPrice_history
        ret.__pnl_history = pnl_history
        ret.__unrealizedPnl_history = unrealizedPnl_history

        return ret
