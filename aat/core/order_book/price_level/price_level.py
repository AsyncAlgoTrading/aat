from collections import deque
from typing import Dict, Optional, List, Tuple, Union

from aat.core.data import Order
from aat.config import OrderType, OrderFlag

from .ro import PriceLevelRO
from ..cpp import _CPP, _make_cpp_price_level


class _PriceLevel(object):
    __slots__ = [
        "_price",
        "_orders",
        "_orders_staged",
        "_orders_filled_staged",
        "_stop_orders",
        "_stop_orders_staged",
        "_collector",
    ]

    def __new__(cls, *args, **kwargs):
        if _CPP:
            return _make_cpp_price_level(*args, **kwargs)
        return super(_PriceLevel, cls).__new__(cls)

    def __init__(self, price, collector):
        self._price = price
        self._orders = deque()
        self._orders_staged = deque()
        self._orders_filled_staged = deque()
        self._stop_orders = []
        self._stop_orders_staged = []
        self._collector = collector

    @property
    def price(self) -> float:
        return self._price

    @property
    def volume(self) -> float:
        return sum((x.volume - x.filled) for x in self._orders)

    def add(self, order) -> None:
        # append order to deque
        if order.order_type == OrderType.STOP:
            if order.stop_target in self._stop_orders:
                return
            self._stop_orders.append(order.stop_target)
        else:
            if order in self._orders:
                # change event
                self._collector.pushChange(order)
            else:
                if order.filled < order.volume:
                    self._orders.append(order)
                    self._collector.pushOpen(order)

    def find(self, order) -> Optional[Order]:
        # check if order is in level
        if order.price != self._price:
            # order not here/not here anymore
            return None

        for o in self._orders:
            if o.id == order.id:
                return o

    def modify(self, order) -> Order:
        # check if order is in level
        if order.price != self._price or order.id not in (o.id for o in self._orders):
            # something is wrong
            raise Exception(f"Order not found in price level {self._price}: {order}")

        # modify order
        for o in self._orders:
            if o.id == order.id:
                # only allowed to modify volume
                o.volume = order.volume

        # trigger cancel event
        self._collector.pushChange(order)

        # return the order
        return order

    def remove(self, order) -> Order:
        # check if order is in level
        if order.price != self._price or order not in self._orders:
            # something is wrong
            raise Exception(f"Order not found in price level {self._price}: {order}")

        # remove order
        self._orders.remove(order)

        # trigger cancel event
        self._collector.pushCancel(order)

        # return the order
        return order

    def cross(self, taker_order) -> Tuple[Optional[Order], List[Order]]:
        """Cross the spread

        Args:
            taker_order (Order): the order crossing the spread
        Returns:
            order (Order or None): the order crossing, if there is some remaining
            secondary_orders (List[Order] or None): Orders that get triggered as a result of the crossing (e.g. stop orders)
        """
        if taker_order.order_type == OrderType.STOP:
            self.add(taker_order)
            return None, ()

        if taker_order.filled == taker_order.volume:
            # already filled:
            return None, self._get_stop_orders()

        elif taker_order.filled > taker_order.volume:
            raise Exception("Unknown error occurred - order book is corrupt")

        while (taker_order.filled < taker_order.volume) and self._orders:
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

                    # won't fill anything from that order
                    self._orders_filled_staged.append(0.0)
                    continue

                else:
                    # maker_order is partially executed
                    maker_order.filled += to_fill

                    # append filled in case need to revert
                    self._orders_filled_staged.append(to_fill)

                    # will exit loop
                    taker_order.filled = taker_order.volume
                    self._collector.pushFill(taker_order)

                    # change event
                    self._collector.pushChange(maker_order, True, to_fill)

                    if maker_order.flag == OrderFlag.IMMEDIATE_OR_CANCEL:
                        # cancel maker event, don't put in queue
                        self._collector.pushCancel(maker_order)
                    else:
                        # push back in deque
                        self._orders.appendleft(maker_order)

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
                    maker_order.filled = maker_order.volume

                    # append filled in case need to revert
                    self._orders_filled_staged.append(maker_order.volume)

                    # don't append to deque
                    # tell maker order filled
                    self._collector.pushChange(taker_order)
                    self._collector.pushFill(maker_order, True, maker_remaining)

            else:
                # exactly equal
                maker_order.filled += to_fill
                taker_order.filled += maker_remaining

                # append filled in case need to revert
                self._orders_filled_staged.append(to_fill)

                self._collector.pushFill(taker_order)
                self._collector.pushFill(maker_order, True, to_fill)

        if taker_order.filled == taker_order.volume:
            # execute the taker order
            self._collector.pushTrade(taker_order, taker_order.filled)

            # return nothing to signify to stop
            return None, self._get_stop_orders()

        elif taker_order.filled > taker_order.volume:
            raise Exception("Unknown error occurred - order book is corrupt")

        # return order, this level is cleared and the order still has volume
        return taker_order, self._get_stop_orders()

    def clear(self) -> None:
        """clear queues"""
        self._orders.clear()
        self._orders_staged.clear()
        self._orders_filled_staged.clear()
        self._stop_orders = []
        self._stop_orders_staged = []

    def _get_stop_orders(self) -> List[Order]:
        if self._stop_orders:
            self._stop_orders_staged = self._stop_orders.copy()
            self._stop_orders = []
            return self._stop_orders_staged
        return []

    def commit(self) -> None:
        """staged orders accepted, clear"""
        self.clear()

    def revert(self) -> None:
        """staged order reverted, unstage the orders"""
        assert len(self._orders) == 0

        # reset orders
        self._orders = self._orders_staged

        # deduct filled amount
        for i, filled in enumerate(self._orders_filled_staged):
            self._orders[i].filled -= filled

        # reset staged
        self._orders_staged = deque()
        self._orders_filled_staged = deque()

        # reset stop_orders
        self._stop_orders = self._stop_orders_staged

        # reset staged
        self._stop_orders_staged = []

    def __bool__(self) -> bool:
        """use deque size as truth value"""
        return len(self._orders) > 0

    def __iter__(self):
        """iterate through orders"""
        for order in self._orders:
            yield order

    def __len__(self) -> int:
        """get number of orders"""
        return len(self._orders)

    def __getitem__(self, index):
        """get item"""
        return self._orders[index]

    def ro(self) -> PriceLevelRO:
        return PriceLevelRO(self.price, self.volume, len(self))

    def toDict(self) -> Dict[str, Union[int, float]]:
        raise NotImplementedError()
