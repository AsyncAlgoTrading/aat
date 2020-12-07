from .handler import EventHandler
from ..data import Event


class PrintHandler(EventHandler):
    #########################
    # Event Handler Methods #
    #########################
    async def onTrade(self, event: Event) -> None:
        """Called whenever a `Trade` event is received"""
        print(event)

    async def onOrder(self, event: Event) -> None:
        """Called whenever an Order `Open` event is received"""
        print(event)

    async def onData(self, event: Event) -> None:
        """Called whenever other data is received"""
        print(event)

    async def onHalt(self, event: Event) -> None:
        """Called whenever an exchange `Halt` event is received, i.e. an event to stop trading"""
        print(event)

    async def onContinue(self, event: Event) -> None:
        """Called whenever an exchange `Continue` event is received, i.e. an event to continue trading"""
        print(event)

    async def onError(self, event: Event) -> None:
        """Called whenever an internal error occurs"""
        print(event)

    async def onStart(self, event: Event) -> None:
        """Called once at engine initialization time"""
        print(event)

    async def onExit(self, event: Event) -> None:
        """Called once at engine exit time"""
        print(event)
