from abc import ABCMeta
from typing import List
from aat.core import Order, Position

# from abc import ABCMeta, abstractmethod


class _OrderEntry(metaclass=ABCMeta):
    """internal only class to represent the rest-sink
    side of a data source"""

    async def accounts(self) -> List[Position]:  # TODO List[Account] ?
        """get accounts from source"""
        return []

    async def balance(self) -> List[Position]:
        """get cash balance"""
        return []

    async def newOrder(self, order: Order) -> bool:
        """submit a new order to the exchange. should set the given order's `id` field to exchange-assigned id

        Returns:
            True if order received
            False if order rejected

        For MarketData-only, can just return False/None
        """
        raise NotImplementedError()

    async def cancelOrder(self, order: Order) -> bool:
        """cancel a previously submitted order to the exchange.

        Returns:
            True if order received
            False if order rejected

        For MarketData-only, can just return False/None
        """
        raise NotImplementedError()
