import sys


from aat.core import Order
from ..handler import EventHandler


class Manager(EventHandler):
    def __init__(self, trading_engine, trading_type, exchanges):
        '''The Manager sits between the strategies and the engine and manages state'''
        self._risk_mgr = trading_engine.risk_manager
        self._order_mgr = trading_engine.order_manager

        for exc in exchanges:
            self._order_mgr.addExchange(exc)

    # *********************
    # Order Entry Methods *
    # *********************
    def orders(self):
        raise NotImplementedError()

    def pastOrders(self):
        raise NotImplementedError()

    def trades(self):
        raise NotImplementedError()

    async def newOrder(self, order: Order, strategy):
        ret = await self._risk_mgr.newOrder(order, strategy)
        # TODO check risk
        ret = await self._order_mgr.newOrder(order, strategy)
        return ret
    # *********************

    # *********************
    # Risk Methods        *
    # *********************
    def positions(self, instrument=None, exchange=None, side=None):
        return self._risk_mgr.positions(instrument=instrument, exchange=exchange, side=side)

    def risk(self, position=None):
        return self._risk_mgr.risk(position=position)
    # **********************

    # **********************
    # EventHandler methods *
    # **********************

    async def onTrade(self, event):
        await self._risk_mgr.onTrade(event)
        await self._order_mgr.onTrade(event)

    async def onOpen(self, event):
        await self._risk_mgr.onOpen(event)
        await self._order_mgr.onOpen(event)

    async def onCancel(self, event):
        await self._risk_mgr.onCancel(event)
        await self._order_mgr.onCancel(event)

    async def onChange(self, event):
        await self._risk_mgr.onChange(event)
        await self._order_mgr.onChange(event)

    async def onFill(self, event):
        await self._risk_mgr.onFill(event)
        await self._order_mgr.onFill(event)

    async def onHalt(self, event):
        await self._risk_mgr.onHalt(event)

    async def onContinue(self, event):
        await self._risk_mgr.onContinue(event)

    async def onData(self, event):
        # TODO
        pass

    async def onError(self, event):
        # TODO
        print('\n\nA Fatal Error has occurred')
        print(event.target)
        sys.exit(1)

    async def onExit(self, event):
        # TODO
        pass

    async def onStart(self, event):
        # TODO
        pass
