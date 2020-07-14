from abc import ABCMeta, abstractmethod


class _MarketData(metaclass=ABCMeta):
    '''internal only class to represent the streaming-source
    side of a data source'''
    @abstractmethod
    def instruments(self):
        '''get list of available instruments'''

    @abstractmethod
    async def tick(self):
        '''return data from exchange'''
