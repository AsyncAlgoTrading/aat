from collections import deque
from ..models import Event, Trade
from ...common import _in_cpp
from ...config import EventType


try:
    from aat.binding import _CollectorCpp  # type: ignore
    _CPP = _in_cpp()
except ImportError:
    _CPP = False


def _make_cpp_collector(callback=lambda *args: args):
    '''helper method to ensure all arguments are setup'''
    return _CollectorCpp(callback)


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

    def __new__(cls, *args, **kwargs):
        if _CPP:
            return _make_cpp_collector(*args, **kwargs)
        return super(_Collector, cls).__new__(cls)

    def __init__(self, callback=lambda *args: args):
        # callback to call to process events
        self._callback = callback

        # queue of events to trigger
        self._event_queue = deque()

        # queue of orders that are included in the trade
        self._orders = deque()

        # the taker order
        self._taker_order = None

        # price levels to clear, if we commit
        self._price_levels = deque()

        # reset status
        self.reset()

    ####################
    # State Management #
    ####################
    def reset(self):
        self._event_queue.clear()
        self._price = 0.0
        self._volume = 0.0
        self._price_levels.clear()
        self._orders.clear()
        self._taker_order = None

    def setCallback(self, callback):
        self._callback = callback

    def push(self, event):
        '''push event to queue'''
        self._event_queue.append(event)

    def pushOpen(self, order):
        '''push order open'''
        self.push(Event(type=EventType.OPEN, target=order))

    def pushFill(self, order, accumulate=False):
        '''push order fill'''
        if accumulate:
            self.accumulate(order)
        self.push(Event(type=EventType.FILL, target=order))

    def pushChange(self, order, accumulate=False):
        '''push order change'''
        if accumulate:
            self.accumulate(order)
        self.push(Event(type=EventType.CHANGE, target=order))

    def pushCancel(self, order, accumulate=False):
        '''push order cancellation'''
        if accumulate:
            self.accumulate(order)
        self.push(Event(type=EventType.CANCEL,
                        target=order))

    def pushTrade(self, taker_order):
        '''push taker order trade'''
        if not self.orders():
            raise Exception('No maker orders provided')

        if taker_order.filled <= 0:
            raise Exception('No trade occurred')

        if taker_order.volume < self.volume():
            raise Exception('Accumulation error occurred')

        self.push(Event(type=EventType.TRADE,
                        target=Trade(volume=self.volume(),
                                     price=self.price(),
                                     maker_orders=self.orders().copy(),
                                     taker_order=taker_order)))

        self._taker_order = taker_order

    def accumulate(self, order):
        # FIXME price change/volume down?
        self._price = ((self._price * self._volume + order.price * order.filled) / (self._volume + order.filled)) if (self._volume + order.filled > 0) else 0.0
        self._volume += order.filled
        self._orders.append(order)

    def clearLevel(self, price_level):
        self._price_levels.append(price_level)
        return len(self._price_levels)

    def commit(self):
        '''flush the event queue'''
        while self._event_queue:
            ev = self._event_queue.popleft()
            self._callback(ev)

        for pl in self._price_levels:
            pl.commit()

        # reset order volume/filled
        for order in self.orders():
            order.rebase()

        # reset order volume/filled
        if self.taker_order():
            self.taker_order().rebase()

        self.reset()

    def revert(self):
        '''revert the event queue'''
        for pl in self._price_levels:
            pl.revert()

        for order in self.orders():
            order.filled = 0.0

        self.reset()

    def clear(self):
        '''clear the event queue'''
        self.reset()
    ####################

    ###############
    # Order Stats #
    ###############
    def price(self):
        '''VWAP'''
        return self._price

    def volume(self):
        '''volume'''
        return self._volume

    def orders(self):
        return self._orders

    def taker_order(self):
        return self._taker_order

    def events(self):
        return self._event_queue

    def price_levels(self):
        return self._price_levels

    def clearedLevels(self):
        return len(self._price_levels)
