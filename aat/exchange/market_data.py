from abc import ABCMeta, abstractmethod


class _MarketData(metaclass=ABCMeta):
    '''internal only class to represent the streaming-source
    side of a data source'''

    @abstractmethod
    async def tick(self):
        '''return data from exchange'''
