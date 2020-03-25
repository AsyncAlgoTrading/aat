from ..core import Data
from abc import ABCMeta, abstractmethod


class Strategy(metaclass=ABCMeta):
    @abstractmethod
    def onTrade(self, data: Data):
        '''onTrade'''

    @abstractmethod
    def onOpen(self, data: Data):
        '''onOpen'''

    @abstractmethod
    def onFill(self, resp: Data):
        '''onFill'''

    @abstractmethod
    def onCancel(self, data: Data):
        '''onCancel'''

    @abstractmethod
    def onChange(self, data: Data):
        '''onChange'''

    @abstractmethod
    def onError(self, data: Data):
        '''onError'''

    def onStart(self):
        '''onStart'''
        pass

    def onExit(self):
        '''onExit'''
        pass

    def onAnalyze(self, engine):
        '''onAnalyze'''
        pass

    def onHalt(self, data):
        '''onHalt'''
        pass

    def onContinue(self, data):
        '''onContinue'''
        pass

