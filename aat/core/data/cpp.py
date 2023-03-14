import logging
from collections import deque
from datetime import datetime
from typing import TYPE_CHECKING, Any, List, Optional

from aat.common import _in_cpp
from aat.config import EventType, OrderFlag, OrderType, Side

from ..exchange import ExchangeType
from ..instrument import Instrument

if TYPE_CHECKING:
    from .order import Order


try:
    from aat.binding import DataCpp, EventCpp, OrderCpp, TradeCpp  # type: ignore

    _CPP = _in_cpp()

except ImportError:
    logging.critical("Could not load C++ extension")
    DataCpp, EventCpp, OrderCpp, TradeCpp = object, object, object, object
    _CPP = False


def _make_cpp_data(
    id: str,
    timestamp: datetime,
    instrument: Instrument,
    exchange: ExchangeType,
    data: Any,
) -> DataCpp:
    """helper method to ensure all arguments are setup"""
    return DataCpp(id, timestamp, instrument, exchange, data)


def _make_cpp_event(type: EventType, target: Any) -> EventCpp:
    """helper method to ensure all arguments are setup"""
    return EventCpp(type, target)


def _make_cpp_order(
    volume: float,
    price: float,
    side: Side,
    instrument: Instrument,
    exchange: ExchangeType = ExchangeType(""),
    notional: float = 0.0,
    order_type: OrderType = OrderType.MARKET,
    flag: OrderFlag = OrderFlag.NONE,
    stop_target: Optional["Order"] = None,
    id: Optional[str] = None,
    timestamp: Optional[datetime] = None,
) -> OrderCpp:
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


def _make_cpp_trade(
    id: str,
    timestamp: datetime,
    maker_orders: Optional[List["Order"]] = None,
    taker_order: Optional["Order"] = None,
) -> TradeCpp:
    """helper method to ensure all arguments are setup"""
    return TradeCpp(id, timestamp, maker_orders or deque(), taker_order)
