import sys


from aat.core import Order
from ..handler import EventHandler


class Manager(EventHandler):
    def __init__(self, trading_engine, trading_type, exchanges):
        '''The Manager sits between the strategies and the engine and manages state'''
        self._order_mgr = trading_engine.order_manager
        self._risk_mgr = trading_engine.risk_manager
        self._exec_mgr = trading_engine.execution_manager

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

    def newOrder(self, order: Order, strategy):
        self._order_mgr.newOrder(order, strategy)
    # *********************

    # **********************
    # EventHandler methods *
    # **********************
    def onTrade(self, event):
        # TODO
        self._order_mgr.onTrade(event)

    def onOpen(self, event):
        # TODO
        pass

    def onCancel(self, event):
        # TODO
        pass

    def onChange(self, event):
        # TODO
        pass

    def onFill(self, event):
        # TODO
        pass

    def onHalt(self, event):
        # TODO
        pass

    def onContinue(self, event):
        # TODO
        pass

    def onData(self, event):
        # TODO
        pass

    def onError(self, event):
        # TODO
        print('\n\nA Fatal Error has occurred')
        print(event.target)
        sys.exit(1)

    def onExit(self, event):
        # TODO
        pass

    def onStart(self, event):
        # TODO
        pass
