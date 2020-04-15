from abc import ABCMeta
from typing import List
from ..core import Order
# from abc import ABCMeta, abstractmethod


class _OrderEntry(metaclass=ABCMeta):
    '''internal only class to represent the rest-sink
    side of a data source'''

    def accounts(self) -> List:
        '''get accounts from source'''
        return []

    def sendOrder(self, order: Order):
        '''send order to exchange'''
