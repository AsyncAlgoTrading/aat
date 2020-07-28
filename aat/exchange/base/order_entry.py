from abc import ABCMeta
from typing import List
from ...core import Order
# from abc import ABCMeta, abstractmethod


class _OrderEntry(metaclass=ABCMeta):
    '''internal only class to represent the rest-sink
    side of a data source'''

    def accounts(self) -> List:
        '''get accounts from source'''
        return []

    async def newOrder(self, order: Order):
        '''submit a new order to the exchange. should set the given order's `id` field to exchange-assigned id

        For MarketData-only, can just return None
        '''
        raise NotImplementedError()

    async def cancelOrder(self, order: Order):
        '''cancel a previously submitted order to the exchange.

        For MarketData-only, can just return None
        '''
        raise NotImplementedError()
