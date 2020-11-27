from aat.core.exchange import ExchangeType
from aat.common import _in_cpp


try:
    from aat.binding import _CollectorCpp  # type: ignore
    from aat.binding import OrderBookCpp  # type: ignore
    from aat.binding import _PriceLevelCpp  # type: ignore

    _CPP = _in_cpp()
except ImportError:
    _CPP = False


def _make_cpp_collector(callback=lambda *args: args):
    """helper method to ensure all arguments are setup"""
    return _CollectorCpp(callback)


def _make_cpp_orderbook(instrument, exchange_name="", callback=lambda x: print(x)):
    """helper method to ensure all arguments are setup"""
    return OrderBookCpp(instrument, exchange_name or ExchangeType(""), callback)


def _make_cpp_price_level(price, collector):
    """helper method to ensure all arguments are setup"""
    return _PriceLevelCpp(price, collector)
