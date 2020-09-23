from abc import ABCMeta, abstractmethod
from inspect import isabstract
from typing import TYPE_CHECKING
from ..models import Event
from ...config import EventType

if TYPE_CHECKING:
    # Circular import
    from aat.engine import StrategyManager


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
            {
                # Market data
                EventType.TRADE: self._valid_callback('onTrade'),
                EventType.OPEN: (self._valid_callback('onOpen'), self._valid_callback('onOrder')),
                EventType.CANCEL: (self._valid_callback('onCancel'), self._valid_callback('onOrder')),
                EventType.CHANGE: (self._valid_callback('onChange'), self._valid_callback('onOrder')),
                EventType.FILL: (self._valid_callback('onFill'), self._valid_callback('onOrderEvent')),
                EventType.DATA: self._valid_callback('onData'),
                EventType.HALT: self._valid_callback('onHalt'),
                EventType.CONTINUE: self._valid_callback('onContinue'),
                EventType.ERROR: self._valid_callback('onError'),
                EventType.START: self._valid_callback('onStart'),
                EventType.EXIT: self._valid_callback('onExit'),

                # Order Entry
                EventType.BOUGHT: (self._valid_callback('onBought'), self._valid_callback('onTraded')),
                EventType.SOLD: (self._valid_callback('onSold'), self._valid_callback('onTraded')),
                EventType.REJECTED: self._valid_callback('onRejected'),
                EventType.CANCELED: self._valid_callback('onCanceled'),
            }.get(event_type, None)

    ################################################
    # Event Handler Methods                        #
    #                                              #
    # NOTE: these should all be of the form onNoun #
    ################################################

    @abstractmethod
    async def onTrade(self, event: Event) -> None:
        '''Called whenever a `Trade` event is received'''

    async def onOrder(self, event: Event) -> None:
        '''Called whenever an Order `Open`, `Cancel`, `Change`, or `Fill` event is received'''
        pass

    async def onOpen(self, event: Event) -> None:
        '''Called whenever an Order `Open` event is received'''
        pass

    async def onCancel(self, event: Event) -> None:
        '''Called whenever an Order `Cancel` event is received'''
        pass

    async def onChange(self, event: Event) -> None:
        '''Called whenever an Order `Change` event is received'''
        pass

    async def onFill(self, event: Event) -> None:
        '''Called whenever an Order `Fill` event is received'''
        pass

    async def onData(self, event: Event) -> None:
        '''Called whenever other data is received'''

    async def onHalt(self, event: Event) -> None:
        '''Called whenever an exchange `Halt` event is received, i.e. an event to stop trading'''
        pass

    async def onContinue(self, event: Event) -> None:
        '''Called whenever an exchange `Continue` event is received, i.e. an event to continue trading'''
        pass

    async def onError(self, event: Event) -> None:
        '''Called whenever an internal error occurs'''
        pass

    async def onStart(self, event: Event) -> None:
        '''Called once at engine initialization time'''
        pass

    async def onExit(self, event: Event) -> None:
        '''Called once at engine exit time'''
        pass

    ################################################
    # Order Entry Callbacks                        #
    #                                              #
    # NOTE: these should all be of the form onVerb #
    ################################################
    async def onBought(self, event: Event):
        '''Called on my order bought'''
        pass

    async def onSold(self, event: Event):
        '''Called on my order sold'''
        pass

    async def onTraded(self, event: Event):
        '''Called on my order bought or sold'''
        pass

    async def onRejected(self, event: Event):
        '''Called on my order rejected'''
        pass

    async def onCanceled(self, event: Event):
        '''Called on my order canceled'''
        pass

    #################
    # Other Methods #
    #################


setattr(EventHandler.onTrade, '_original', 1)
setattr(EventHandler.onOrder, '_original', 1)
setattr(EventHandler.onOpen, '_original', 1)
setattr(EventHandler.onCancel, '_original', 1)
setattr(EventHandler.onChange, '_original', 1)
setattr(EventHandler.onFill, '_original', 1)
setattr(EventHandler.onData, '_original', 1)
setattr(EventHandler.onHalt, '_original', 1)
setattr(EventHandler.onContinue, '_original', 1)
setattr(EventHandler.onError, '_original', 1)
setattr(EventHandler.onStart, '_original', 1)
setattr(EventHandler.onExit, '_original', 1)

setattr(EventHandler.onBought, '_original', 1)
setattr(EventHandler.onSold, '_original', 1)
setattr(EventHandler.onRejected, '_original', 1)
setattr(EventHandler.onTraded, '_original', 1)
