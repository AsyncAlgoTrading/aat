from .collector import _Collector
from .price_level import _PriceLevel
from .utils import _insort
from ..exchange import ExchangeType
from ...config import Side, OrderFlag, OrderType
from ...common import _in_cpp

try:
    from aat.binding import OrderBookCpp  # type: ignore
    _CPP = _in_cpp()
except ImportError:
    _CPP = False


def _make_cpp_orderbook(instrument, exchange_name='', callback=lambda x: print(x)):
    '''helper method to ensure all arguments are setup'''
    return OrderBookCpp(instrument, exchange_name or ExchangeType(''), callback)


class OrderBook(object):
    '''A limit order book.

    Supports the following order types:
        - [x] market
            - [x] executes the entire volume
            - [ ] if notional specified, will execute (price*volume) worth (e.g. relies on total price, not volume)

            Flags:
                - [x] no flag
                - [x] fill-or-kill: entire order must fill against current book, otherwise nothing fills
                - [x] all-or-none: entire order must fill against 1 order, otherwise nothing fills
                - [x] immediate-or-cancel: same as fill or kill

        - [x] limit
            - [x] either puts on book or crosses spread, by default puts remainder on book

            Flags:
                - [x] no flag
                - [x] fill-or-kill: entire order must fill against current book, otherwise cancelled
                - [x] all-or-none: entire order must fill against 1 order, otherwise cancelled
                - [x] immediate-or-cancel: whenever this order executes, fill whatever fills and cancel remaining

        - [x] stop-market
            - 0 volume order, but when crosses triggers the submission of a market order
        - [x] stop-limit
            - 0 volume order, but when crosses triggers the submission of a market order

    Supports the following order flags:
        - [x] no flag
        - [x] fill-or-kill
        - [x] all-or-none
        - [x] immediate-or-cancel

    Args:
        instrument (Instrument): the instrument for the book
        exchange_name (str): name of the exchange
        callback (Function): callback on events
    '''
    def __new__(cls, *args, **kwargs):
        if _CPP:
            return _make_cpp_orderbook(*args, **kwargs)
        return super(OrderBook, cls).__new__(cls)

    def __init__(self,
                 instrument,
                 exchange_name='',
                 callback=print):

        self._instrument = instrument
        self._exchange_name = exchange_name or ExchangeType('')

        # levels look like [10, 10.5, 11, 11.5]
        self._buy_levels = []
        self._sell_levels = []

        # look like {price level: PriceLevel}
        self._buys = {}
        self._sells = {}

        # setup collector for conditional orders
        self._collector = _Collector(callback)

    def setCallback(self, callback):
        self._collector.setCallback(callback)

    def _clearOrders(self, order, amount):
        '''internal'''
        if order.side == Side.BUY:
            self._sell_levels = self._sell_levels[amount:]
        else:
            self._buy_levels = self._buy_levels[:-amount] if amount else self._buy_levels

    def _getTop(self, side, cleared):
        '''internal'''
        return (self._sell_levels[cleared] if len(self._sell_levels) > cleared else None) if side == Side.BUY else (self._buy_levels[-1 - cleared] if len(self._buy_levels) > cleared else None)

    def add(self, order):
        '''add a new order to the order book, potentially triggering events:
            EventType.TRADE: if this order crosses the book and fills orders
            EventType.FILL: if this order crosses the book and fills orders
            EventType.CHANGE: if this order crosses the book and partially fills orders
        Args:
            order (Data): order to submit to orderbook
        '''
        if order is None:
            raise Exception('Order cannot be None')

        # secondary triggered orders
        secondaries = []

        # get the top price on the opposite side of book
        top = self._getTop(order.side, self._collector.clearedLevels())

        # set levels to the right side
        levels = self._buy_levels if order.side == Side.BUY else self._sell_levels
        prices = self._buys if order.side == Side.BUY else self._sells
        prices_cross = self._sells if order.side == Side.BUY else self._buys

        # set order price appropriately
        if order.order_type == OrderType.MARKET:
            if order.flag in (None, OrderFlag.NONE):
                # price goes infinite "fill however you want"
                order_price = float('inf') if order.side == Side.BUY else float('-inf')
            else:
                # with a flag, the price dictates the "max allowed price" to AON or FOK under
                order_price = order.price
        else:
            order_price = order.price

        # check if crosses
        while top is not None and (order_price >= top if order.side == Side.BUY else order_price <= top):
            # execute order against level
            # if returns trade, it cleared the level
            # else, order was fully executed
            trade, secondary = prices_cross[top].cross(order)

            if secondary:
                # append to secondaries
                secondaries.extend(secondary)

            if trade:
                # clear sell level
                top = self._getTop(order.side, self._collector.clearLevel(prices_cross[top]))
                continue

            # trade is done, check if level was cleared exactly
            if not prices_cross[top]:
                # level cleared exactly
                self._collector.clearLevel(prices_cross[top])
            break

        # if order remaining, check rules/push to book
        if order.filled < order.volume:
            if order.order_type == OrderType.MARKET:
                # Market orders
                if order.flag in (OrderFlag.ALL_OR_NONE, OrderFlag.FILL_OR_KILL):
                    # cancel the order, do not execute any
                    self._collector.revert()

                    # cancel the order
                    self._collector.pushCancel(order)
                    self._collector.commit()
                else:
                    # market order, partial
                    if order.filled > 0:
                        self._collector.pushTrade(order, order.filled)

                    # clear levels
                    self._clearOrders(order, self._collector.clearedLevels())

                    # execute order, cancel the rest
                    self._collector.pushCancel(order)
                    self._collector.commit()

                    # execute secondaries
                    for secondary in secondaries:
                        secondary.timestamp = order.timestamp  # adjust trigger time
                        self.add(secondary)

            else:
                # Limit Orders
                if order.flag == OrderFlag.FILL_OR_KILL:
                    if order.filled > 0:
                        # reverse partial
                        # cancel the order, do not execute any
                        self._collector.revert()

                        # reset filled
                        order.filled = 0.0

                        # cancel the order
                        self._collector.pushCancel(order)
                        self._collector.commit()
                    else:
                        # add to book
                        self._collector.commit()

                        # limit order, put on books
                        if _insort(levels, order.price):
                            # new price level
                            prices[order.price] = _PriceLevel(order.price, collector=self._collector)

                        # add order to price level
                        prices[order.price].add(order)

                        # execute secondaries
                        for secondary in secondaries:
                            secondary.timestamp = order.timestamp  # adjust trigger time
                            self.add(secondary)

                elif order.flag == OrderFlag.ALL_OR_NONE:
                    if order.filled > 0:
                        # order could not fill fully, revert
                        # cancel the order, do not execute any
                        self._collector.revert()

                        # reset filled
                        order.filled = 0.0

                        # cancel the order
                        self._collector.pushCancel(order)
                        self._collector.commit()

                    else:
                        # add to book
                        self._collector.commit()

                        # limit order, put on books
                        if _insort(levels, order.price):
                            # new price level
                            prices[order.price] = _PriceLevel(order.price, collector=self._collector)

                        # add order to price level
                        prices[order.price].add(order)

                        # execute secondaries
                        for secondary in secondaries:
                            secondary.timestamp = order.timestamp  # adjust trigger time
                            self.add(secondary)

                elif order.flag == OrderFlag.IMMEDIATE_OR_CANCEL:
                    if order.filled > 0:
                        # clear levels
                        self._clearOrders(order, self._collector.clearedLevels())

                        # execute the ones that filled, kill the remainder
                        self._collector.pushCancel(order)

                        # commit
                        self._collector.commit()

                        # execute secondaries
                        for secondary in secondaries:
                            secondary.timestamp = order.timestamp  # adjust trigger time
                            self.add(secondary)

                    else:
                        # add to book
                        self._collector.commit()

                        # limit order, put on books
                        if _insort(levels, order.price):
                            # new price level
                            prices[order.price] = _PriceLevel(order.price, collector=self._collector)

                        # add order to price level
                        prices[order.price].add(order)

                        # execute secondaries
                        for secondary in secondaries:
                            secondary.timestamp = order.timestamp  # adjust trigger time
                            self.add(secondary)

                else:
                    # clear levels
                    self._clearOrders(order, self._collector.clearedLevels())

                    # execute order
                    self._collector.commit()

                    # limit order, put on books
                    if _insort(levels, order.price):
                        # new price level
                        prices[order.price] = _PriceLevel(order.price, collector=self._collector)

                    # add order to price level
                    prices[order.price].add(order)

                    # execute secondaries
                    for secondary in secondaries:
                        secondary.timestamp = order.timestamp  # adjust trigger time
                        self.add(secondary)
        else:
            if order.filled > order.volume:
                raise Exception("Unknown error occurred - order book is corrupt")

            # don't need to add trade as this is done in the price_levels
            # clear levels
            self._clearOrders(order, self._collector.clearedLevels())

            # execute all the orders
            self._collector.commit()

            # execute secondaries
            for secondary in secondaries:
                secondary.timestamp = order.timestamp  # adjust trigger time
                self.add(secondary)

        # clear the collector
        self._collector.clear()

    def change(self, order):
        '''modify an order on the order book, potentially triggering events:
            EventType.CHANGE: the change event for this
        Args:
            order (Data): order to submit to orderbook
        '''
        assert order.volume > 0.0  # otherwise use cancel

        price = order.price
        side = order.side
        levels = self._buy_levels if side == Side.BUY else self._sell_levels
        prices = self._buys if side == Side.BUY else self._sells

        if price not in levels:
            raise Exception('Orderbook out of sync')

        # modify order in price level
        prices[price].modify(order)

    def cancel(self, order):
        '''remove an order from the order book, potentially triggering events:
            EventType.CANCEL: the cancel event for this
        Args:
            order (Data): order to submit to orderbook
        '''
        price = order.price
        side = order.side
        levels = self._buy_levels if side == Side.BUY else self._sell_levels
        prices = self._buys if side == Side.BUY else self._sells

        if price not in levels:
            raise Exception('Orderbook out of sync')

        # remove order from price level
        prices[price].remove(order)

        # delete level if no more volume
        if not prices[price]:
            levels.remove(price)

    def find(self, order):
        '''find an order in the order book
        Args:
            order (Data): order to find in orderbook
        '''
        price = order.price
        side = order.side
        levels = self._buy_levels if side == Side.BUY else self._sell_levels
        prices = self._buys if side == Side.BUY else self._sells

        if price not in levels:
            return None

        # find order from price level
        return prices[price].find(order)

    def topOfBook(self):
        '''return top of both sides

        Args:

        Returns:
            value (dict): returns {BUY: tuple, SELL: tuple}
        '''
        return {Side.BUY: [self._buy_levels[-1], self._buys[self._buy_levels[-1]].volume()] if len(self._buy_levels) > 0 else [0, 0],
                Side.SELL: [self._sell_levels[0], self._sells[self._sell_levels[0]].volume()] if len(self._sell_levels) > 0 else [float('inf'), 0]}

    def spread(self):
        '''return the spread

        Args:

        Returns:
            value (float): spread between bid and ask
        '''
        tob = self.topOfBook()
        return tob[Side.SELL] - tob[Side.BUY]

    def level(self, level: int = 0, price: float = None):
        '''return book level

        Args:
            level (int): depth of book to return
            price (float): price level to look for
        Returns:
            value (tuple): returns ask or bid if Side specified, otherwise ask,bid
        '''
        # collect bids and asks at `level`
        if price is not None:
            bid = self._buys[price] if price in self._buy_levels else None
            ask = self._sells[price] if price in self._sell_levels else None
        else:
            bid = [self._buy_levels[-level - 1], self._buys[self._buy_levels[-level - 1]].volume()] if len(self._buy_levels) > level else [0.0, 0.0]
            ask = [self._sell_levels[level], self._sells[self._sell_levels[level]].volume()] if len(self._sell_levels) > level else [0.0, 0.0]
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

        ret = {}
        ret[Side.BUY] = []
        ret[Side.SELL] = []
        for _ in range(levels):
            ask, bid = self.level(_)
            if ask:
                ret[Side.SELL].append(ask)

            if bid:
                ret[Side.BUY].append(bid)
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
                if self._sells[level]:
                    sells[-1].append(self._sells[level])
                    count -= 1

        # reverse so visually upside down
        sells.reverse()

        # show top 5 levels, then group next 5, 10, 20, etc
        # buys second
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
                if self._buys[level]:
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
