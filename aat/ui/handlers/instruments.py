import tornado.gen
from ...enums import ExchangeType
from .base import HTTPHandler
from tornado.concurrent import run_on_executor
from perspective import PerspectiveHTTPMixin


class InstrumentsHandler(PerspectiveHTTPMixin, HTTPHandler):
    '''Server Handler
    Extends:
        HTTPHandler
    '''

    def initialize(self, trading_engine, psp_kwargs=None):
        self.te = trading_engine
        self.psp_kwargs = psp_kwargs or {}

    @run_on_executor
    def get_data(self, exchange, **psp_kwargs):
        if exchange:
            exchange = ExchangeType(exchange)
        msgs = [x.to_dict(True, True) for x in self.te.query.query_instruments(exchange)]
        super(InstrumentsHandler, self).loadData(data=msgs, **psp_kwargs)
        return super(InstrumentsHandler, self).getData()

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        exchange = self.get_argument('exchange', '')
        dat = yield self.get_data(exchange, **self.psp_kwargs)
        self.write(dat)
