from aat.config import Side
from aat.core import Event, Order, Instrument, ExchangeType


class RiskManager(object):
    def __init__(self):
        pass

    def positions(self, instrument: Instrument = None, exchange: ExchangeType = None, side: Side = None):
        return "positions"

    def risk(self, position=None):
        return "risk"

    async def newOrder(self, order: Order, strategy):
        # TODO
        pass

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
