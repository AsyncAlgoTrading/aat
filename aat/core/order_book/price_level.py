from collections import deque


class _PriceLevel(object):
    def __init__(self, price, collector):
        self._price = price
        self._orders = deque()
        self._collector = collector

    def price(self):
        return self._price

    def volume(self):
        return sum((x.volume - x.filled) for x in self._orders)

    def add(self, order):
        # append order to deque
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
        self._collector.pushCanncel(order)

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
                self._collector.pushFill(taker_order)
                self._collector.pushChange(maker_order, accumulate=True)

            elif maker_remaining < to_fill:
                # maker_order is fully executed
                # don't append to deque
                # tell maker order filled
                taker_order.filled += maker_remaining
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
            return None

        # return order, this level is cleared and the order still has volume
        return taker_order

    def clear(self):
        self._orders.clear()

    def __bool__(self):
        '''use deque size as truth value'''
        return len(self._orders) > 0

    def __iter__(self):
        '''iterate through orders'''
        for order in self._orders:
            yield order
