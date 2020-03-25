import bisect
from collections import deque
from datetime import datetime
from .models import Data, Event, Trade
from ..config import Side, EventType, DataType


def _insort(a, x):
    '''insert x into a if not currently there'''
    i = bisect.bisect_left(a, x)
    if i != len(a) and a[i] == x:
        # don't insert
        return False
    a.insert(i, x)
    return True


class _PriceLevel(object):
    def __init__(self, price, callback):
        self._price = price
        self._orders = deque()
        self._on_event = callback

    def setCallback(self, callback):
        self._on_event = callback

    def price(self):
        return self._price

    def volume(self):
        return sum((x.volume - x.filled) for x in self._orders)

    def add(self, order):
        # append order to deque
        if order in self._orders:
            # change event
            self._on_event(Event(type=EventType.CHANGE, target=order))
        else:
            self._orders.append(order)
            self._on_event(Event(type=EventType.OPEN, target=order))

    def remove(self, order):
        # check if order is in level
        if order.price != self._price or order not in self._orders:
            # something is wrong
            raise Exception(f'Order not found in price leve {self._price}: {order}')

        # remove order
        self._orders.remove(order)

        # trigger cancel event
        self._on_event(Event(type=EventType.CANCEL, target=order))

        # return the order
        return order

    def cross(self, taker_order):
        if taker_order.filled >= taker_order.volume:
            # already filled:
            return None

        while taker_order.filled < taker_order.volume and self._orders:
            # need to fill original volume - filled so far
            to_fill = taker_order.volume - taker_order.filled

            # pop maker order from list
            maker_order = self._orders.popleft()

            # remaining in maker_order
            maker_remaining = maker_order.volume - maker_order.filled

            if maker_remaining > to_fill:
                # maker_order is partially executed
                maker_order.filled += to_fill

                # push back in deque
                self._orders.appendleft(maker_order)

                # will exit loop
                self._on_event(Event(type=EventType.FILL, target=taker_order))
                self._on_event(Event(type=EventType.CHANGE, target=maker_order))
            elif maker_remaining < to_fill:
                # maker_order is fully executed
                # don't append to deque
                # tell maker order filled
                taker_order.filled += maker_remaining
                self._on_event(Event(type=EventType.CHANGE, target=taker_order))
                self._on_event(Event(type=EventType.FILL, target=maker_order))
            else:
                # exactly equal
                maker_order.filled += to_fill
                taker_order.filled += maker_remaining
                self._on_event(Event(type=EventType.FILL, target=taker_order))
                self._on_event(Event(type=EventType.FILL, target=maker_order))

        if taker_order.filled >= taker_order.volume:
            # execute the taker order
            self._on_event(Event(type=EventType.TRADE,
                                 target=Trade(timestamp=datetime.now().timestamp(),
                                              instrument=taker_order.instrument,
                                              price=maker_order.price,
                                              volume=to_fill,
                                              side=taker_order.side,
                                              maker_order=maker_order,
                                              taker_order=taker_order,
                                              exchange=maker_order.exchange)))
            # return nothing to signify to stop
            return None

        # return order, this level is cleared and the order still has volume
        return taker_order

    def __bool__(self):
        '''use deque size as truth value'''
        return len(self._orders) > 0

    def __iter__(self):
        '''iterate through orders'''
        for order in self._orders:
            yield order

class OrderBook(object):
    def __init__(self,
                 instrument,
                 exchange_name='',
                 callback=print):

        self._instrument = instrument
        self._exchange_name = exchange_name

        # levels look like [10, 10.5, 11, 11.5]
        self._buy_levels = []
        self._sell_levels = []

        # look like {price level: PriceLevel}
        self._buys = {}
        self._sells = {}

        # setup callback
        self._callback = callback

    def setCallback(self, callback):
        self._callback = callback
        for sell_level in self._sell_levels:
            self._sells[sell_level].setCallback(callback)
        for buy_level in self._buy_levels:
            self._buys[buy_level].setCallback(callback)

    def add(self, order):
        '''add a new order to the order book, potentially triggering events:
            EventType.TRADE: if this order crosses the book and fills orders
            EventType.FILL: if this order crosses the book and fills orders
            EventType.CHANGE: if this order crosses the book and partially fills orders
        Args:
            order (Data): order to submit to orderbook
        '''
        if order.side == Side.BUY:
            # order is buy, so look at top of sell side
            top = self._sell_levels[0] if len(self._sell_levels) > 0 else float('inf')

            cleared = []

            # check if crosses
            while order.price >= top:
                # execute order against level
                # if returns trade, it cleared the level
                # else, order was fully executed
                trade = self._sells[top].cross(order)

                if trade:
                    # clear sell level
                    cleared.append(top)
                    top = self._sell_levels[len(cleared)] if len(self._sell_levels) > len(cleared) else float('inf')
                    continue

                # trade is done, check if level was cleared exactly
                if not self._sells[top]:
                    # level cleared exactly
                    cleared.append(top)
                break

            # clear levels
            self._sell_levels = self._sell_levels[len(cleared):]

            # if order remaining, push to book
            if order.filled < order.volume:
                # push to book
                if _insort(self._buy_levels, order.price):
                    # new price level
                    self._buys[order.price] = _PriceLevel(order.price, self._callback)

                # add order to price level
                self._buys[order.price].add(order)

        else:
            # order is sell, so look at top of buy side
            top = self._buy_levels[-1] if len(self._buy_levels) > 0 else 0

            cleared = []

            # check if crosses
            while order.price <= top:
                # execute order against level
                # if returns trade, it cleared the level
                # else, order was fully executed
                trade = self._buys[top].cross(order)

                if trade:
                    # clear sell level
                    cleared.append(top)
                    top = self._buy_levels[-1 - len(cleared)] if len(self._buy_levels) > len(cleared) else 0
                    continue

                # trade is done, check if level was cleared exactly
                if not self._buys[top]:
                    # level cleared exactly
                    cleared.append(top)
                break

            # clear levels
            self._buy_levels = self._buy_levels[:-len(cleared)] if len(cleared) else self._buy_levels

            # if order remaining, push to book
            if order.filled < order.volume:
                # push to book
                if _insort(self._sell_levels, order.price):
                    # new price level
                    self._sells[order.price] = _PriceLevel(order.price, self._callback)

                # add order to price level
                self._sells[order.price].add(order)

    def cancel(self, order):
        '''remove an order from the order book, potentially triggering events:
            EventType.CANCEL: the cancel event for this
        Args:
            order (Data): order to submit to orderbook
        '''
        price = order.price
        side = order.side

        if side == Side.BUY:
            if price not in self._buy_levels:
                raise Exception('Orderbook out of sync!')
            self._buys[price].remove(order)

            # delete level if no more volume
            if not self._buys[price]:
                self._buy_levels.remove(price)
        else:
            if price not in self._sell_levels:
                raise Exception('Orderbook out of sync!')
            self._sells[price].remove(order)

            # delete level if no more volume
            if not self._sells[price]:
                self._sell_levels.remove(price)

    def topOfBook(self):
        '''return top of both sides
        
        Args:
            
        Returns:
            value (dict): returns {'bid': tuple, 'ask': tuple}
        '''
        return {'bid': (self._buy_levels[-1], self._buys[self._buy_levels[-1]].volume()) if len(self._buy_levels) > 0 else (0, 0),
                'ask': (self._sell_levels[0], self._sells[self._sell_levels[0]].volume()) if len(self._sell_levels) > 0 else (float('inf'), 0)}

    def spread(self):
        '''return the spread

        Args:

        Returns:
            value (float): spread between bid and ask
        '''
        tob = self.topOfBook()
        return tob['ask'] - tob['bid']

    def level(self, level=0, price=None, side=None):
        '''return book level
        
        Args:
            level (int): depth of book to return
            price (float): price level to look for
            side (Side): side to return, or None to return both
        Returns:
            value (tuple): returns ask or bid if Side specified, otherwise ask,bid
        '''
        # collect bids and asks at `level`
        if price:
            bid = (self._buys[price], self._buys[price].volume()) if price in self._buy_levels else None
            ask = (self._sells[price], self._sells[price].volume()) if price in self._sell_levels else None
        else:
            bid = (self._buy_levels[-level], self._buys[self._buy_levels[-level]].volume()) if len(self._buy_levels) > level else None
            ask = (self._sell_levels[level], self._sells[self._sell_levels[level]].volume()) if len(self._sell_levels) > level else None

        if side == Side.SELL:
            return ask
        elif side == Side.BUY:
            return bid
        return ask, bid

    def levels(self, levels=0):
        '''return book levels starting at top
        
        Args:
            levels (int): number of levels to return
        Returns:
            value (dict of list): returns {"ask": [levels in order], "bid": [levels in order]} for `levels` number of levels
        '''
        if levels <= 0:
            return self.topOfBook()

        ret = self.topOfBook()
        ret['bid'] = [ret['bid']]
        ret['ask'] = [ret['ask']]
        for _ in range(levels):
            ask, bid = self.level(_)
            if ask:
                ret['ask'].append(ask)
            if bid:
                ret['bid'].append(bid)
        return ret

    def __iter__(self):
        '''iterate through asks then bids by level'''
        for level in self._sell_levels:
            for order in self._sells[level]:
                yield order
        for level in self._buy_levels:
            for order in self._buys[level]:
                yield order

    def __repr__(self):
        ret = ''
        # show top 5 levels, then group next 5, 10, 20, etc
        # sells first
        sells = []
        count = 5
        orig = 5
        for i, level in enumerate(self._sell_levels):
            if i < 5:
                # append to list
                sells.append(self._sells[level])
            else:
                if count == orig:
                    sells.append([])
                elif count == 0:
                    # double orig and restart
                    orig = orig * 2
                    count = orig
                # append to last list
                sells[-1].append(self._sells[level])
                count -= 1

        # reverse so visually upside down
        sells.reverse()

        # show top 5 levels, then group next 5, 10, 20, etc
        # sells first
        buys = []
        count = 5
        orig = 5
        for i, level in enumerate(reversed(self._buy_levels)):
            if i < 5:
                # append to list
                buys.append(self._buys[level])
            else:
                if count == orig:
                    buys.append([])
                if count == 0:
                    # double orig and restart
                    orig = orig * 2
                    count = orig
                # append to last list
                buys[-1].append(self._buys[level])
                count -= 1

        # sell list, then line, then buy list
        # if you hit a list, give aggregate
        ret = ''

        # format the sells on top, tabbed to the right, with price\tvolume
        for item in sells:
            if isinstance(item, list):
                # just aggregate these upper levels
                if len(item) > 1:
                    ret += f'\t\t{item[0].price():.2f} - {item[-1].price():.2f}\t{sum(i.volume() for i in item):.2f}'
                else:
                    ret += f'\t\t{item[0].price():.2f}\t\t{item[0].volume():.2f}'
            else:
                ret += f'\t\t{item.price():.2f}\t\t{item.volume():.2f}'
            ret += '\n'

        ret += '-----------------------------------------------------\n'

        # format the buys on bottom, tabbed to the left, with volume\tprice so prices align
        for item in buys:
            if isinstance(item, list):
                # just aggregate these lower levels
                if len(item) > 1:
                    ret += f'{sum(i.volume() for i in item):.2f}\t\t{item[0].price():.2f} - {item[-1].price():.2f}\t'
                else:
                    ret += f'{item[0].volume():.2f}\t\t{item[0].price():.2f}'
            else:
                ret += f'{item.volume():.2f}\t\t{item.price():.2f}'
            ret += '\n'

        return ret
