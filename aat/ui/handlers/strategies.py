import tornado.gen
from .base import HTTPHandler
from tornado.concurrent import run_on_executor
from perspective import PerspectiveHTTPMixin


class StrategiesHandler(PerspectiveHTTPMixin, HTTPHandler):
    '''Server Handler
    Extends:
        tornado.web.RequestHandler
    '''
    def initialize(self, trading_engine, **psp_kwargs):
        self.te = trading_engine
        self.psp_kwargs = psp_kwargs

    @run_on_executor
    def get_data(self, **psp_kwargs):
        dat = [s.to_dict() for s in self.te.strategies()]
        super(StrategiesHandler, self).loadData(data=dat, **psp_kwargs)
        return super(StrategiesHandler, self).getData()

    @tornado.gen.coroutine
    def get(self):
        dat = yield self.get_data(**self.psp_kwargs)
        self.write(dat)
