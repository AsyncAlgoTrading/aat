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
        self._price_levels.clear()
        self._orders.clear()


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
            print(taker_order, taker_order.filled)
            print(self.orders(), [x.filled for x in self.orders()])
            print(self.volume())
            raise Exception('Accumulation error occurred')

        self.push(Event(type=EventType.TRADE,
                        target=Trade(volume=self.volume(),
                                     price=self.price(),
                                     maker_orders=self.orders().copy(),
                                     taker_order=taker_order)))

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

        for order in self._orders:
            if order.volume > order.filled:
                # reset
                print('resetting order ', order, order.volume, order.filled)
                volume = order.volume - order.filled
                order.filled = 0
                order.volume = volume
            elif order.volume == order.filled:
                print('resetting order ', order, order.volume, order.filled)
                order.filled = 0
                # order.volume = 0

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
