from ..core import Event
from abc import ABCMeta, abstractmethod


class Strategy(metaclass=ABCMeta):
    @abstractmethod
    def onTrade(self, event: Event):
        '''Called whenever a `Trade` event is received'''

    @abstractmethod
    def onOpen(self, event: Event):
        '''Called whenever an Order `Open` event is received'''

    @abstractmethod
    def onFill(self, event: Event):
        '''Called whenever an Order `Fill` event is received'''

    @abstractmethod
    def onCancel(self, event: Event):
        '''Called whenever an Order `Cancel` event is received'''

    @abstractmethod
    def onChange(self, event: Event):
        '''Called whenever an Order `Change` event is received'''

    @abstractmethod
    def onError(self, event: Event):
        '''Called whenever an internal error occurs'''

    def onStart(self):
        '''Called once at engine initialization time'''
        pass

    def onExit(self):
        '''Called once at engine exit time'''
        pass

    def onHalt(self, data):
        '''Called whenever an exchange `Halt` event is received, i.e. an event to stop trading'''
        pass

    def onContinue(self, data):
        '''Called whenever an exchange `Continue` event is received, i.e. an event to continue trading'''
        pass

    def onAnalyze(self, engine):
        '''Called once after engine exit to analyze the results of a backtest'''
        pass
