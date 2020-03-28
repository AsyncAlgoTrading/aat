from datetime import datetime
from collections import deque
from ..models import Event, Trade
from ...config import EventType


class _Collector(object):
    def __init__(self, callback):
        self._callback = callback
        self._event_queue = deque()
        self._orders = deque()
        self.reset()

    def reset(self):
        self._event_queue.clear()
        self._price = 0.0
        self._volume = 0.0
        self._orders.clear()

    def setCallback(self, callback):
        self._callback = callback

    def push(self, event):
        '''push event to queue'''
        self._event_queue.append(event)

    def accumulate(self, order):
        self._price = (self._price * self._volume + order.price * order.volume) / (self._volume + order.volume)
        self._volume += order.volume
        self._orders.append(order)

    def flush(self):
        '''flush the event queue'''
        while self._event_queue:
            ev = self._event_queue.popleft()
            self._callback(ev)
        self.reset()

    def clear(self):
        '''clear the event queue'''
        self.reset()

    def price(self):
        '''VWAP'''
        return self._price

    def volume(self):
        '''volume'''
        return self._volume

    def orders(self):
        '''orders'''
        return self._orders

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
