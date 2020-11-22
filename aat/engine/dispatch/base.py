from abc import abstractmethod
from typing import Optional
from aat.core import Event
from aat.core.handler import EventHandler


class ManagerBase(EventHandler):
    @abstractmethod
    def _setManager(self, mgr):
        """set the root manager"""

    async def onBought(  # type: ignore[override]
        self, event: Event, strategy: Optional[EventHandler]
    ):
        """Called on my order bought"""
        pass

    async def onSold(  # type: ignore[override]
        self, event: Event, strategy: Optional[EventHandler]
    ):
        """Called on my order sold"""
        pass

    async def onTraded(  # type: ignore[override]
        self, event: Event, strategy: Optional[EventHandler]
    ):
        """Called on my order bought or sold"""
        pass

    async def onReceived(  # type: ignore[override]
        self, event: Event, strategy: Optional[EventHandler]
    ):
        """Called on my order received"""
        pass

    async def onRejected(  # type: ignore[override]
        self, event: Event, strategy: Optional[EventHandler]
    ):
        """Called on my order rejected"""
        pass

    async def onCanceled(  # type: ignore[override]
        self, event: Event, strategy: Optional[EventHandler]
    ):
        """Called on my order canceled"""
        pass
