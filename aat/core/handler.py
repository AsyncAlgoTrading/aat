from ..config import EventType
from .models import Event
from abc import ABCMeta, abstractmethod
from inspect import isabstract


class EventHandler(metaclass=ABCMeta):
    def _valid_callback(self, callback):
        if hasattr(self, callback) and not isabstract(callback) and not hasattr(getattr(self, callback), "_original"):
            return getattr(self, callback)
        return None

    def callback(self, event_type):
        return \
            {EventType.TRADE: self._valid_callback('onTrade'),
             EventType.OPEN: self._valid_callback('onOpen'),
             EventType.CANCEL: self._valid_callback('onCancel'),
             EventType.CHANGE: self._valid_callback('onChange'),
             EventType.FILL: self._valid_callback('onFill'),
             EventType.DATA: self._valid_callback('onData'),
             EventType.HALT: self._valid_callback('onHalt'),
             EventType.CONTINUE: self._valid_callback('onContinue'),
             EventType.ERROR: self._valid_callback('onError'),
             EventType.START: self._valid_callback('onStart'),
             EventType.EXIT: self._valid_callback('onExit')} \
            .get(event_type, None)

    @abstractmethod
    def onTrade(self, event: Event):
        '''Called whenever a `Trade` event is received'''

    @abstractmethod
    def onOpen(self, event: Event):
        '''Called whenever an Order `Open` event is received'''
        pass

    @abstractmethod
    def onFill(self, event: Event):
        '''Called whenever an Order `Fill` event is received'''
        pass

    @abstractmethod
    def onCancel(self, event: Event):
        '''Called whenever an Order `Cancel` event is received'''
        pass

    @abstractmethod
    def onChange(self, event: Event):
        '''Called whenever an Order `Change` event is received'''
        pass

    @abstractmethod
    def onError(self, event: Event):
        '''Called whenever an internal error occurs'''
        pass

    @abstractmethod
    def onStart(self):
        '''Called once at engine initialization time'''
        pass

    @abstractmethod
    def onExit(self):
        '''Called once at engine exit time'''
        pass

    @abstractmethod
    def onHalt(self, data):
        '''Called whenever an exchange `Halt` event is received, i.e. an event to stop trading'''
        pass

    @abstractmethod
    def onContinue(self, data):
        '''Called whenever an exchange `Continue` event is received, i.e. an event to continue trading'''
        pass

    @abstractmethod
    def onData(self, event: Event):
        '''Called whenever other data is received'''

    def onAnalyze(self, engine):
        '''Called once after engine exit to analyze the results of a backtest'''
        pass


class PrintHandler(EventHandler):
    def onTrade(self, event: Event):
        '''Called whenever a `Trade` event is received'''
        print(event)

    def onOpen(self, event: Event):
        '''Called whenever an Order `Open` event is received'''
        print(event)

    def onFill(self, event: Event):
        '''Called whenever an Order `Fill` event is received'''
        print(event)

    def onCancel(self, event: Event):
        '''Called whenever an Order `Cancel` event is received'''
        print(event)

    def onChange(self, event: Event):
        '''Called whenever an Order `Change` event is received'''
        print(event)

    def onError(self, event: Event):
        '''Called whenever an internal error occurs'''
        print(event)

    def onStart(self, event: Event):
        '''Called once at engine initialization time'''
        print(event)

    def onExit(self, event: Event):
        '''Called once at engine exit time'''
        print(event)

    def onHalt(self, event: Event):
        '''Called whenever an exchange `Halt` event is received, i.e. an event to stop trading'''
        print(event)

    def onContinue(self, event: Event):
        '''Called whenever an exchange `Continue` event is received, i.e. an event to continue trading'''
        print(event)

    def onData(self, event: Event):
        '''Called whenever other data is received'''
        print(event)
