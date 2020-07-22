from abc import ABCMeta, abstractmethod
from inspect import isabstract
from typing import TYPE_CHECKING
from .models import Event
from ..config import EventType

if TYPE_CHECKING:
    # Circular import
    from .engine.manager import StrategyManager


class EventHandler(metaclass=ABCMeta):
    _manager: 'StrategyManager'

    def _setManager(self, mgr: 'StrategyManager'):
        self._manager = mgr

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
             EventType.EXIT: self._valid_callback('onExit'),
             EventType.BOUGHT: self._valid_callback('onBought'),
             EventType.SOLD: self._valid_callback('onSold'),
             EventType.REJECTED: self._valid_callback('onRejected')} \
            .get(event_type, None)

    #########################
    # Event Handler Methods #
    #########################

    @abstractmethod
    async def onTrade(self, event: Event) -> None:
        '''Called whenever a `Trade` event is received'''

    @abstractmethod
    async def onOpen(self, event: Event) -> None:
        '''Called whenever an Order `Open` event is received'''
        pass

    @abstractmethod
    async def onCancel(self, event: Event) -> None:
        '''Called whenever an Order `Cancel` event is received'''
        pass

    @abstractmethod
    async def onChange(self, event: Event) -> None:
        '''Called whenever an Order `Change` event is received'''
        pass

    @abstractmethod
    async def onFill(self, event: Event) -> None:
        '''Called whenever an Order `Fill` event is received'''
        pass

    @abstractmethod
    async def onData(self, event: Event) -> None:
        '''Called whenever other data is received'''

    @abstractmethod
    async def onHalt(self, event: Event) -> None:
        '''Called whenever an exchange `Halt` event is received, i.e. an event to stop trading'''
        pass

    @abstractmethod
    async def onContinue(self, event: Event) -> None:
        '''Called whenever an exchange `Continue` event is received, i.e. an event to continue trading'''
        pass

    @abstractmethod
    async def onError(self, event: Event) -> None:
        '''Called whenever an internal error occurs'''
        pass

    @abstractmethod
    async def onStart(self, event: Event) -> None:
        '''Called once at engine initialization time'''
        pass

    @abstractmethod
    async def onExit(self, event: Event) -> None:
        '''Called once at engine exit time'''
        pass

    #########################
    # Order Entry Callbacks #
    #########################
    async def onBought(self, event: Event):
        '''Called on my order bought'''
        pass

    async def onSold(self, event: Event):
        '''Called on my order sold'''
        pass

    async def onRejected(self, event: Event):
        '''Called on my order rejected'''
        pass

    #################
    # Other Methods #
    #################


class PrintHandler(EventHandler):
    #########################
    # Event Handler Methods #
    #########################
    def onTrade(self, event: Event):
        '''Called whenever a `Trade` event is received'''
        print(event)

    def onOpen(self, event: Event):
        '''Called whenever an Order `Open` event is received'''
        print(event)

    def onCancel(self, event: Event):
        '''Called whenever an Order `Cancel` event is received'''
        print(event)

    def onChange(self, event: Event):
        '''Called whenever an Order `Change` event is received'''
        print(event)

    def onFill(self, event: Event):
        '''Called whenever an Order `Fill` event is received'''
        print(event)

    def onData(self, event: Event):
        '''Called whenever other data is received'''
        print(event)

    def onHalt(self, event: Event):
        '''Called whenever an exchange `Halt` event is received, i.e. an event to stop trading'''
        print(event)

    def onContinue(self, event: Event):
        '''Called whenever an exchange `Continue` event is received, i.e. an event to continue trading'''
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
