from abc import ABCMeta
from typing import List
# from abc import ABCMeta, abstractmethod


class _OrderEntry(metaclass=ABCMeta):
    '''internal only class to represent the rest-sink
    side of a data source'''

    def accounts(self) -> List:
        '''get accounts from source'''
        return []
