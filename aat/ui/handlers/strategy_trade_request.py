import tornado.gen
from .base import HTTPHandler
from tornado.concurrent import run_on_executor
from perspective import PerspectiveHTTPMixin


class StrategyTradeRequestHandler(PerspectiveHTTPMixin, HTTPHandler):
    '''Server Handler
    Extends:
        HTTPHandler
    '''

    def initialize(self, trading_engine, psp_kwargs=None):
        self.te = trading_engine
        self.psp_kwargs = psp_kwargs or {}

    @run_on_executor
    def get_data(self, **psp_kwargs):
        msgs = [s.to_dict(True, True) for s in self.te.query.query_tradereqs()]
        if len(msgs) > 0:
            for msg in msgs:
                msg['underlying'] = msg['instrument']['underlying']
                msg['instrument'] = msg['instrument']['underlying'] + ',' + msg['instrument']['type']

        super(StrategyTradeRequestHandler, self).loadData(data=msgs, **psp_kwargs)
        return super(StrategyTradeRequestHandler, self).getData()

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        dat = yield self.get_data(**self.psp_kwargs)
        self.write(dat)
