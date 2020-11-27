import logging
from collections import deque
from datetime import datetime

from aat.common import _in_cpp
from aat.core import ExchangeType
from aat.config import OrderType, OrderFlag

try:
    from aat.binding import DataCpp, EventCpp, OrderCpp, TradeCpp  # type: ignore

    _CPP = _in_cpp()

except ImportError:
    logging.critical("Could not load C++ extension")
    _CPP = False


def _make_cpp_data(id, timestamp, instrument, exchange, data):
    """helper method to ensure all arguments are setup"""
    return DataCpp(id, timestamp, instrument, exchange, data)


def _make_cpp_event(type, target):
    """helper method to ensure all arguments are setup"""
    return EventCpp(type, target)


def _make_cpp_order(
    volume,
    price,
    side,
    instrument,
    exchange=ExchangeType(""),
    notional=0.0,
    order_type=OrderType.MARKET,
    flag=OrderFlag.NONE,
    stop_target=None,
    id=None,
    timestamp=None,
):
    """helper method to ensure all arguments are setup"""
    return OrderCpp(
        id or "0",
        timestamp or datetime.now(),
        volume,
        price,
        side,
        instrument,
        exchange,
        notional,
        order_type,
        flag,
        stop_target,
    )


def _make_cpp_trade(id, timestamp, maker_orders=None, taker_order=None):
    """helper method to ensure all arguments are setup"""
    return TradeCpp(id, timestamp, maker_orders or deque(), taker_order)
