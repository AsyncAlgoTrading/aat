from aat.core import Order


class Manager(object):
    def __init__(self, trading_engine, trading_type, exchanges):
        '''The Manager sits between the strategies and the engine and manages state'''
        self._order_mgr = trading_engine.order_manager
        self._risk_mgr = trading_engine.risk_manager
        self._exec_mgr = trading_engine.execution_manager

        for exc in exchanges:
            self._order_mgr.addExchange(exc)

    def orders(self):
        raise NotImplementedError()

    def pastOrders(self):
        raise NotImplementedError()

    def trades(self):
        raise NotImplementedError()

    def newOrder(self, order: Order):
        self._order_mgr.newOrder(order)
