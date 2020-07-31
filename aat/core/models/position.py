from datetime import datetime

from ..exchange import ExchangeType
from ..instrument import Instrument
from ...common import _in_cpp

try:
    from aat.binding import PositionCpp  # type: ignore
    _CPP = _in_cpp()
except ImportError:
    _CPP = False


class Position(object):
    __slots__ = [
        "__size",
        "__size_history",
        "__notional",
        "__notional_history",
        "__price",
        "__price_history",
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

    def __new__(cls, *args, **kwargs):
        if _CPP:
            return PositionCpp(*args, **kwargs)
        return super(Position, cls).__new__(cls)

    def __init__(self, size, notional, price, timestamp, instrument, exchange, trades):
        assert instrument is None or isinstance(instrument, Instrument)
        assert isinstance(exchange, ExchangeType)

        self.__instrument = instrument
        self.__exchange = exchange

        assert isinstance(size, (int, float))
        assert isinstance(price, (int, float))
        assert isinstance(notional, (int, float))

        self.__size = size
        self.__size_history = [(size, timestamp)]

        self.__notional = notional
        self.__notional_history = [(notional, timestamp)]

        self.__price = price
        self.__price_history = [(price, timestamp)]

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
    def instrument(self):
        return self.__instrument

    @property
    def exchange(self):
        return self.__exchange

    @property
    def sizeHistory(self):
        return self.__size_history

    @property
    def notionalHistory(self):
        return self.__notional_history

    @property
    def priceHistory(self):
        return self.__price_history

    @property
    def instrumentPriceHistory(self):
        return self.__instrumentPrice_history

    @property
    def pnlHistory(self):
        return self.__pnl_history

    @property
    def unrealizedPnlHistory(self):
        return self.__unrealizedPnl_history

    # ***********#
    # Read/write #
    # ***********#
    @property
    def price(self):
        return round(self.__price, 4)

    @price.setter
    def price(self, price):
        '''Tuple as we need temporal information for history'''
        assert isinstance(price, tuple)
        price, when = price

        assert isinstance(price, (int, float))
        assert isinstance(when, datetime)

        self.__price = price
        self.__price_history.append((self.price, when))

    @property
    def instrumentPrice(self):
        return round(self.__instrumentPrice, 4)

    @instrumentPrice.setter
    def instrumentPrice(self, instrument_price):
        '''Tuple as we need temporal information for history'''
        assert isinstance(instrument_price, tuple)
        instrument_price, when = instrument_price

        assert isinstance(instrument_price, (int, float))
        assert isinstance(when, datetime)

        self.__instrumentPrice = instrument_price
        self.__instrumentPrice_history.append((self.instrumentPrice, when))

    @property
    def size(self):
        return self.__size

    @size.setter
    def size(self, size):
        '''Tuple as we need temporal information for history'''
        assert isinstance(size, tuple)
        size, when = size

        assert isinstance(size, (int, float))
        assert isinstance(when, datetime)

        self.__size = size
        self.__size_history.append((self.size, when))

    @property
    def notional(self):
        return round(self.__notional, 4)

    @notional.setter
    def notional(self, notional):
        '''Tuple as we need temporal information for history'''
        assert isinstance(notional, tuple)
        notional, when = notional

        assert isinstance(notional, (int, float))
        assert isinstance(when, datetime)

        self.__notional = notional
        self.__notional_history.append((self.notional, when))

    @property
    def pnl(self):
        return round(self.__pnl, 4)

    @pnl.setter
    def pnl(self, pnl):
        '''Tuple as we need temporal information for history'''
        assert isinstance(pnl, tuple)
        pnl, when = pnl

        assert isinstance(pnl, (int, float))
        assert isinstance(when, datetime)

        self.__pnl = pnl
        self.__pnl_history.append((self.pnl, when))

    @property
    def unrealizedPnl(self):
        return round(self.__unrealizedPnl, 4)

    @unrealizedPnl.setter
    def unrealizedPnl(self, unrealized_pnl):
        '''Tuple as we need temporal information for history'''
        assert isinstance(unrealized_pnl, tuple)
        unrealized_pnl, when = unrealized_pnl

        assert isinstance(unrealized_pnl, (int, float))
        assert isinstance(when, datetime)

        self.__unrealizedPnl = unrealized_pnl
        self.__unrealizedPnl_history.append((self.unrealizedPnl, when))

    @property
    def trades(self):
        return self.__trades

    def __repr__(self):
        return f'Position(price={self.price}, size={self.size}, notional={self.notional}, pnl={self.pnl}, unrealizedPnl={self.unrealizedPnl}, instrument={self.instrument}, exchange={self.exchange})'
