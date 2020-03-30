from datetime import datetime
from collections import deque
from ..models import Event, Trade
from ...config import EventType


class _Collector(object):
    def __init__(self, callback):
        # callback to call to process events
        self._callback = callback

        # queue of events to trigger
        self._event_queue = deque()

        # queue of orders that are included in the trade
        self._orders = deque()

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
        self._orders.clear()
        self._price_levels.clear()

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
        self.push(Event(type=EventType.TRADE,
                        target=Trade(timestamp=datetime.now().timestamp(),
                                     instrument=taker_order.instrument,
                                     price=self.price(),
                                     volume=self.volume(),
                                     side=taker_order.side,
                                     maker_orders=self.orders(),
                                     taker_order=taker_order,
                                     exchange=taker_order.exchange)))

    def accumulate(self, order):
        self._price = ((self._price * self._volume + order.price * order.filled) / (self._volume + order.filled)) if (self._volume + order.filled > 0) else float('nan')
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
        self.reset()

    def revert(self):
        '''revert the event queue'''
        for pl in self._price_levels:
            pl.revert()
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

    def events(self):
        return self._event_queue

    def price_levels(self):
        return self._price_levels

    def clearedLevels(self):
        return len(self._price_levels)
