from abc import abstractmethod
from typing import Optional
from aat.core import Event
from aat.core.handler import EventHandler


class ManagerBase(EventHandler):
    @abstractmethod
    def _setManager(self, mgr):
        """set the root manager"""

    async def onBought(
        self, event: Event, strategy: Optional[EventHandler]
    ):  # type: ignore[override]
        """Called on my order bought"""
        pass

    async def onSold(
        self, event: Event, strategy: Optional[EventHandler]
    ):  # type: ignore[override]
        """Called on my order sold"""
        pass

    async def onTraded(
        self, event: Event, strategy: Optional[EventHandler]
    ):  # type: ignore[override]
        """Called on my order bought or sold"""
        pass

    async def onReceived(
        self, event: Event, strategy: Optional[EventHandler]
    ):  # type: ignore[override]
        """Called on my order received"""
        pass

    async def onRejected(
        self, event: Event, strategy: Optional[EventHandler]
    ):  # type: ignore[override]
        """Called on my order rejected"""
        pass

    async def onCanceled(
        self, event: Event, strategy: Optional[EventHandler]
    ):  # type: ignore[override]
        """Called on my order canceled"""
        pass
