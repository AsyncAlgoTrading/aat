from ..config import EventType
from .models import Event
from abc import ABCMeta, abstractmethod
from inspect import isabstract


class EventHandler(metaclass=ABCMeta):
    def _valid_callback(self, callback):
        if hasattr(self, callback) and not isabstract(callback):
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
        '''onTrade'''

    @abstractmethod
    def onOpen(self, event: Event):
        '''onOpen'''

    @abstractmethod
    def onCancel(self, event: Event):
        '''onCancel'''

    @abstractmethod
    def onChange(self, event: Event):
        '''onChange'''

    @abstractmethod
    def onFill(self, resp: Event):
        '''onFill'''

    @abstractmethod
    def onData(self, event: Event):
        '''onData'''

    @abstractmethod
    def onHalt(self, event):
        '''onHalt'''
        pass

    @abstractmethod
    def onContinue(self, event):
        '''onContinue'''
        pass

    @abstractmethod
    def onError(self, event: Event):
        '''onError'''
        pass

    @abstractmethod
    def onStart(self):
        '''onStart'''
        pass

    @abstractmethod
    def onExit(self):
        '''onExit'''
        pass

    def onAnalyze(self, engine):
        '''onAnalyze'''
        pass


class PrintHandler(EventHandler):
    def onTrade(self, event: Event):
        '''onTrade'''
        print(event)

    def onOpen(self, event: Event):
        '''onOpen'''
        print(event)

    def onCancel(self, event: Event):
        '''onCancel'''
        print(event)

    def onChange(self, event: Event):
        '''onChange'''
        print(event)

    def onFill(self, event: Event):
        '''onFill'''
        print(event)

    def onData(self, event: Event):
        '''onData'''
        print(event)

    def onHalt(self, event: Event):
        '''onHalt'''
        print(event)

    def onContinue(self, event: Event):
        '''onContinue'''
        print(event)

    def onError(self, event: Event):
        '''onError'''
        print(event)

    def onStart(self, event: Event):
        '''onStart'''
        print(event)

    def onExit(self, event: Event):
        '''onExit'''
        print(event)
