from typing import List
from .trade import Trade
from ..exchange import ExchangeType
from ..instrument import Instrument
from ...common import _in_cpp

try:
    from aat.binding import PositionCpp
    _CPP = _in_cpp()
except ImportError:
    _CPP = False


class Position(object):
    __slots__ = [
        "__size",
        "__notional",
        "__price",
        "__instrument",
        "__exchange",
        "__pnl",
        "__unrealizedPnl",
        "__trades",
    ]

    def __new__(cls, *args, **kwargs):
        if _CPP:
            return PositionCpp(*args, **kwargs)
        return super(Position, cls).__new__(cls)

    def __init__(self, size, notional, price, instrument, exchange, trades):
        assert instrument is None or isinstance(instrument, Instrument)
        assert isinstance(exchange, ExchangeType)
        self.__instrument = instrument
        self.__exchange = exchange

        assert isinstance(size, (int, float))
        assert isinstance(price, (int, float))
        assert isinstance(notional, (int, float))
        self.__size = size
        self.__notional = notional
        self.__price = price

        self.__pnl = 0.0
        self.__unrealizedPnl = 0.0
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

    # ***********#
    # Read/write #
    # ***********#
    @property
    def price(self):
        return self.__price

    @price.setter
    def price(self, price):
        assert isinstance(price, (int, float))
        self.__price = price

    @property
    def size(self):
        return self.__size

    @size.setter
    def size(self, size):
        assert isinstance(size, (int, float))
        self.__size = size

    @property
    def notional(self):
        return self.__notional

    @notional.setter
    def notional(self, notional):
        assert isinstance(notional, (int, float))
        self.__notional = notional

    @property
    def pnl(self):
        return self.__pnl

    @pnl.setter
    def pnl(self, pnl):
        assert isinstance(pnl, (int, float))
        self.__pnl = pnl

    @property
    def unrealizedPnl(self):
        return self.__unrealizedPnl

    @unrealizedPnl.setter
    def unrealizedPnl(self, unrealizedPnl):
        assert isinstance(unrealizedPnl, (int, float))
        self.__unrealizedPnl = unrealizedPnl

    @property
    def trades(self):
        return self.__trades


    def __repr__(self):
        return f'Position(price={self.price}, size={self.size}, notinoal={self.notional}, pnl={self.pnl}, unrealizedPnl={self.unrealizedPnl}, instrument={self.instrument}, exchange={self.exchange})'
