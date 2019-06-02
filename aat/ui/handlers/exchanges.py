import tornado.gen
from .base import HTTPHandler
from tornado.concurrent import run_on_executor
from perspective import PerspectiveHTTPMixin


class ExchangesHandler(PerspectiveHTTPMixin, HTTPHandler):
    '''Server Handler
    Extends:
        HTTPHandler
    '''
    def initialize(self, trading_engine, **psp_kwargs):
        self.te = trading_engine
        self.psp_kwargs = psp_kwargs

    @run_on_executor
    def get_data(self, **psp_kwargs):
        msgs = [{'name': x['exchange'].value,
                 'instruments': ','.join(y.to_dict(True, True)['underlying'] for y in x['instruments'])}
                for x in self.te.query().query_exchanges()]
        super(ExchangesHandler, self).loadData(data=msgs, **psp_kwargs)
        return super(ExchangesHandler, self).getData()

    @tornado.gen.coroutine
    def get(self):
        dat = yield self.get_data(**self.psp_kwargs)
        self.write(dat)
