from ..core import Event, EventHandler
from abc import abstractmethod


class Strategy(EventHandler):
    @abstractmethod
    def onTrade(self, event: Event):
        '''Called whenever a `Trade` event is received'''

    def onOpen(self, event: Event):
        '''Called whenever an Order `Open` event is received'''
        pass

    def onFill(self, event: Event):
        '''Called whenever an Order `Fill` event is received'''
        pass

    def onCancel(self, event: Event):
        '''Called whenever an Order `Cancel` event is received'''
        pass

    def onChange(self, event: Event):
        '''Called whenever an Order `Change` event is received'''
        pass

    def onError(self, event: Event):
        '''Called whenever an internal error occurs'''
        pass

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

    def onData(self, event: Event):
        '''Called whenever other data is received'''
        pass

    def onAnalyze(self, engine):
        '''Called once after engine exit to analyze the results of a backtest'''
        pass


Strategy.onTrade._original = 1
Strategy.onOpen._original = 1
Strategy.onFill._original = 1
Strategy.onCancel._original = 1
Strategy.onChange._original = 1
Strategy.onError._original = 1
Strategy.onStart._original = 1
Strategy.onExit._original = 1
Strategy.onHalt._original = 1
Strategy.onContinue._original = 1
Strategy.onData._original = 1
Strategy.onAnalyze._original = 1
