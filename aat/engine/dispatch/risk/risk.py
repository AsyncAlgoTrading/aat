from typing import Optional, List

from aat.core import Event, Order, Trade, Position
from aat.core.handler import EventHandler
from ..base import ManagerBase


class RiskManager(ManagerBase):
    def __init__(self):
        # Track active (open) orders
        self._active_orders = []

    def _setManager(self, manager):
        '''install manager'''
        self._manager = manager

    def updateAccount(self, positions: List[Position]) -> None:
        '''update positions tracking with a position from the exchange'''
        pass

    def updateCash(self, positions: List[Position]) -> None:
        '''update cash positions from exchange'''
        pass

    # *********************
    # Risk Methods        *
    # *********************
    def risk(self, position=None):
        # TODO
        return "risk"

    # *********************
    # Order Entry Methods *
    # *********************
    async def newOrder(self, strategy, order: Order):
        # TODO
        self._active_orders.append(order)  # TODO use strategy
        return order, True

    # **********************
    # EventHandler methods *
    # **********************
    async def onTrade(self, event: Event):
        # TODO
        pass

    async def onCancel(self, event):
        # TODO
        pass

    async def onOpen(self, event: Event):
        # TODO
        pass

    async def onFill(self, event: Event):
        # TODO
        pass

    async def onChange(self, event: Event):
        # TODO
        pass

    async def onData(self, event: Event):
        # TODO
        pass

    async def onHalt(self, event: Event):
        # TODO
        pass

    async def onContinue(self, event: Event):
        # TODO
        pass

    async def onError(self, event: Event):
        # TODO
        pass

    async def onStart(self, event: Event):
        # TODO
        pass

    async def onExit(self, event: Event):
        # TODO
        pass

    #########################
    # Order Entry Callbacks #
    #########################
    async def onTraded(self, event: Event, strategy: Optional[EventHandler]):  # type: ignore[override]
        trade: Trade = event.target  # type: ignore
        self._active_orders.remove(trade.my_order)

    async def onRejected(self, event: Event, strategy: Optional[EventHandler]):  # type: ignore[override]
        order: Order = event.target  # type: ignore
        self._active_orders.remove(order)

    async def onCanceled(self, event: Event, strategy: Optional[EventHandler]):  # type: ignore[override]
        order: Order = event.target  # type: ignore
        self._active_orders.remove(order)
