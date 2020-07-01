from aat.config import Side
from aat.core import Event, Order, Instrument, ExchangeType


class RiskManager(object):
    def __init__(self):
        self._active_orders = {}
        self._active_positions = {}

    def _setManager(self, manager):
        '''install manager'''
        self._manager = manager

    # *********************
    # Risk Methods        *
    # *********************
    def positions(self, instrument: Instrument = None, exchange: ExchangeType = None, side: Side = None):
        return "positions"

    def risk(self, position=None):
        return "risk"

    # *********************
    # Order Entry Methods *
    # *********************
    async def newOrder(self, strategy, order: Order):
        # TODO
        self._active_orders[order] = strategy
        return order, True

    # **********************
    # EventHandler methods *
    # **********************
    async def onTrade(self, event):
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

    async def onHalt(self, data):
        # TODO
        pass

    async def onContinue(self, data):
        # TODO
        pass

    async def onData(self, event):
        # TODO
        pass

    async def onError(self, event):
        # TODO
        pass

    async def onExit(self, event):
        # TODO
        pass

    async def onStart(self, event):
        # TODO
        pass
