from typing import Callable
from aat.core import ExchangeType, Instrument
from aat.common import _in_cpp

try:
    from aat.binding import _CollectorCpp  # type: ignore
    from aat.binding import OrderBookCpp  # type: ignore
    from aat.binding import _PriceLevelCpp  # type: ignore

    _CPP = _in_cpp()
except ImportError:
    _CPP = False


def _make_cpp_collector(callback: Callable = lambda *args: args) -> _CollectorCpp:
    """helper method to ensure all arguments are setup"""
    return _CollectorCpp(callback)


def _make_cpp_orderbook(
    instrument: Instrument,
    exchange_name: str = "",
    callback: Callable = lambda x: print(x),
) -> OrderBookCpp:
    """helper method to ensure all arguments are setup"""
    return OrderBookCpp(instrument, exchange_name or ExchangeType(""), callback)


def _make_cpp_price_level(price: float, collector: _CollectorCpp) -> _PriceLevelCpp:
    """helper method to ensure all arguments are setup"""
    return _PriceLevelCpp(price, collector)
