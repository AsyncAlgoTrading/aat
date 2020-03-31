from collections import deque
from ...config import OrderType, OrderFlag


class _PriceLevel(object):
    def __init__(self, price, collector):
        self._price = price
        self._orders = deque()
        self._orders_staged = deque()
        self._stop_orders = []
        self._stop_orders_staged = []
        self._collector = collector

    def price(self):
        return self._price

    def volume(self):
        return sum((x.volume - x.filled) for x in self._orders)

    def add(self, order):
        # append order to deque
        if order.order_type in (OrderType.STOP_LIMIT, OrderType.STOP_MARKET):
            if order.stop_target in self._stop_orders:
                return
            print('adding', order)
            self._stop_orders.append(order.stop_target)
        else:
            if order in self._orders:
                # change event
                self._collector.pushChange(order)
            else:
                self._orders.append(order)
                self._collector.pushOpen(order)

    def remove(self, order):
        # check if order is in level
        if order.price != self._price or order not in self._orders:
            # something is wrong
            raise Exception(f'Order not found in price leve {self._price}: {order}')

        # remove order
        self._orders.remove(order)

        # trigger cancel event
        self._collector.pushCancel(order)

        # return the order
        return order

    def cross(self, taker_order):
        '''Cross the spread

        Args:
            taker_order (Order): the order crossing the spread
        Returns:
            order (Order or None): the order crossing, if there is some remaining
            secondary_orders (List[Order] or None): Orders that get triggered as a result of the crossing (e.g. stop orders)
        '''
        if taker_order.order_type in (OrderType.STOP_MARKET, OrderType.STOP_LIMIT):
            self.add(taker_order)
            return None, ()

        if taker_order.filled >= taker_order.volume:
            # already filled:
            return None, self._get_stop_orders()

        while taker_order.filled < taker_order.volume and self._orders:
            # need to fill original volume - filled so far
            to_fill = taker_order.volume - taker_order.filled

            # pop maker order from list
            maker_order = self._orders.popleft()

            # add to staged in case we need to revert
            self._orders_staged.append(maker_order)

            # remaining in maker_order
            maker_remaining = maker_order.volume - maker_order.filled

            if maker_remaining > to_fill:
                # handle fill or kill/all or nothing
                if maker_order.flag in (OrderFlag.FILL_OR_KILL, OrderFlag.ALL_OR_NONE):
                    # kill the maker order and continue
                    self._collector.pushCancel(maker_order)
                    continue

                else:
                    # maker_order is partially executed
                    maker_order.filled += to_fill

                    # will exit loop
                    taker_order.filled = taker_order.volume
                    self._collector.pushFill(taker_order)

                    if maker_order.flag == OrderFlag.IMMEDIATE_OR_CANCEL:
                        # change event
                        self._collector.pushCancel(maker_order)
                    else:
                        # push back in deque
                        self._orders.appendleft(maker_order)

                        # change event
                        self._collector.pushChange(maker_order, accumulate=True)

            elif maker_remaining < to_fill:
                # partially fill it regardles
                # this will either trigger the revert in order_book,
                # or it will be partially executed
                taker_order.filled += maker_remaining

                if taker_order.flag == OrderFlag.ALL_OR_NONE:
                    # taker order can't be filled, push maker back and cancel taker
                    # push back in deque
                    self._orders.appendleft(maker_order)
                    return None, self._get_stop_orders()

                else:
                    # maker_order is fully executed
                    # don't append to deque
                    # tell maker order filled
                    self._collector.pushChange(taker_order)
                    self._collector.pushFill(maker_order, accumulate=True)

            else:
                # exactly equal
                maker_order.filled += to_fill
                taker_order.filled += maker_remaining

                self._collector.pushFill(taker_order)
                self._collector.pushFill(maker_order, accumulate=True)

        if taker_order.filled >= taker_order.volume:
            # execute the taker order
            self._collector.pushTrade(taker_order)

            # return nothing to signify to stop
            return None, self._get_stop_orders()

        # return order, this level is cleared and the order still has volume
        return taker_order, self._get_stop_orders()

    def clear(self):
        '''clear queues'''
        self._orders.clear()
        self._orders_staged.clear()
        self._stop_orders = []
        self._stop_orders_staged = []

    def _get_stop_orders(self):
        if self._stop_orders:
            self._stop_orders_staged = self._stop_orders.copy()
            self._stop_orders = []
            return self._stop_orders_staged
        return []

    def commit(self):
        '''staged orders accepted, clear'''
        self.clear()

    def revert(self):
        '''staged order reverted, unstage the orders'''
        self._orders = self._orders_staged
        self._orders_staged = deque()
        self._stop_orders = self._stop_orders_staged
        self._stop_orders_staged = []

    def __bool__(self):
        '''use deque size as truth value'''
        return len(self._orders) > 0

    def __iter__(self):
        '''iterate through orders'''
        for order in self._orders:
            yield order
