from aat.core import Order


class Dispatcher(object):
    def __init__(self, trading_engine):
        '''The Dispatcher sits between the strategies and the engine and manages state'''
        self._order_mgr = trading_engine.order_manager
        self._risk_mgr = trading_engine.risk_manager
        self._exec_mgr = trading_engine.execution_manager

    def openOrders(self):
        raise NotImplementedError()

    def pastOrders(Self):
        raise NotImplementedError()

    def request(self, order: Order):
        self._order_mgr.request(order)

