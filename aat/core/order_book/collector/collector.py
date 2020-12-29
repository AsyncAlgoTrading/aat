from collections import deque
from typing import Any, Callable, Deque, Optional, Type, TYPE_CHECKING

from aat.core.data import Event, Trade, Order
from aat.config import EventType

from ..cpp import _CPP, _make_cpp_collector


if TYPE_CHECKING:
    from ..price_level import _PriceLevel


class _Collector(object):
    __slots__ = [
        "_callback",
        "_event_queue",
        "_orders",
        "_taker_order",
        "_price_levels",
        "_price",
        "_volume",
    ]

    def __new__(cls: Type, *args: Any, **kwargs: Any) -> "_Collector":
        if _CPP:
            return _make_cpp_collector(*args, **kwargs)
        return super(_Collector, cls).__new__(cls)

    def __init__(self, callback: Callable = lambda *args: args):
        # callback to call to process events
        self._callback = callback

        # queue of events to trigger
        self._event_queue: Deque[Event] = deque()

        # queue of orders that are included in the trade
        self._orders: Deque[Order] = deque()

        # the taker order
        self._taker_order: Optional[Order] = None

        # price levels to clear, if we commit
        self._price_levels: Deque["_PriceLevel"] = deque()

        # reset status
        self.reset()

    ####################
    # State Management #
    ####################
    def reset(self) -> None:
        self._event_queue.clear()
        self._price = 0.0
        self._volume = 0.0
        self._price_levels.clear()
        self._orders.clear()
        self._taker_order = None

    def setCallback(self, callback: Callable) -> None:
        self._callback = callback

    def push(self, event: Event) -> None:
        """push event to queue"""
        self._event_queue.append(event)

    def pushOpen(self, order: Order) -> None:
        """push order open"""
        self.push(Event(type=EventType.OPEN, target=order))

    def pushFill(
        self, order: Order, accumulate: bool = False, filled_in_txn: float = 0.0
    ) -> None:
        """push order fill"""
        if accumulate:
            self.accumulate(order, filled_in_txn)
        self.push(Event(type=EventType.FILL, target=order))

    def pushChange(
        self, order: Order, accumulate: bool = False, filled_in_txn: float = 0.0
    ) -> None:
        """push order change"""
        if accumulate:
            self.accumulate(order, filled_in_txn)
        self.push(Event(type=EventType.CHANGE, target=order))

    def pushCancel(
        self, order: Order, accumulate: bool = False, filled_in_txn: float = 0.0
    ) -> None:
        """push order cancellation"""
        if accumulate:
            self.accumulate(order, filled_in_txn)
        self.push(Event(type=EventType.CANCEL, target=order))

    def pushTrade(self, taker_order: Order, filled_in_txn: float) -> None:
        """push taker order trade"""
        if not self.orders:
            raise Exception("No maker orders provided")

        if taker_order.filled <= 0:
            raise Exception("No trade occurred")

        if filled_in_txn != self.volume:
            raise Exception("Accumulation error occurred")

        self.push(
            Event(
                type=EventType.TRADE,
                target=Trade(
                    volume=self.volume,
                    price=self.price,
                    maker_orders=list(self.orders.copy()),
                    taker_order=taker_order,
                ),
            )
        )

        self._taker_order = taker_order

    def accumulate(self, order: Order, filled_in_txn: float) -> None:
        assert filled_in_txn > 0

        # FIXME price change/volume down?
        self._price = (
            (
                (self._price * self._volume + order.price * filled_in_txn)
                / (self._volume + filled_in_txn)
            )
            if (self._volume + filled_in_txn > 0)
            else 0.0
        )
        self._volume += filled_in_txn
        self._orders.append(order)

    def clearLevel(self, price_level: "_PriceLevel") -> int:
        self._price_levels.append(price_level)
        return len(self._price_levels)

    def commit(self) -> None:
        """flush the event queue"""
        while self._event_queue:
            ev = self._event_queue.popleft()
            self._callback(ev)

        for pl in self._price_levels:
            pl.commit()

        self.reset()

    def revert(self) -> None:
        """revert the event queue"""
        for pl in self._price_levels:
            pl.revert()

        self.reset()

    def clear(self) -> None:
        """clear the event queue"""
        self.reset()

    ####################

    ###############
    # Order Stats #
    ###############
    @property
    def price(self) -> float:
        """VWAP"""
        return self._price

    @property
    def volume(self) -> float:
        """volume"""
        return self._volume

    @property
    def orders(self) -> Deque[Order]:
        return self._orders

    @property
    def taker_order(self) -> Optional[Order]:
        return self._taker_order

    @property
    def events(self) -> Deque[Event]:
        return self._event_queue

    @property
    def price_levels(self) -> Deque["_PriceLevel"]:
        return self._price_levels

    def clearedLevels(self) -> int:
        return len(self._price_levels)
