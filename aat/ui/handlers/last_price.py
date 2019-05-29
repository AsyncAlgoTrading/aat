import tornado.gen
from .base import HTTPHandler
from tornado.concurrent import run_on_executor
from perspective import PerspectiveHTTPMixin


class LastPriceHandler(PerspectiveHTTPMixin, HTTPHandler):
    '''Server Handler
    Extends:
        HTTPHandler
    '''
    def initialize(self, trading_engine, **psp_kwargs):
        self.te = trading_engine
        self.psp_kwargs = psp_kwargs

    @run_on_executor
    def get_data(self, **psp_kwargs):
        msgs = [s.to_dict(True, True) for s in self.te.query().query_lastpriceall()]
        if len(msgs) > 0:
            for msg in msgs:
                msg['underlying'] = msg['instrument']['underlying']
                msg['instrument'] = msg['instrument']['underlying'] + ',' + msg['instrument']['type']

        super(LastPriceHandler, self).loadData(data=msgs, **psp_kwargs)
        return super(LastPriceHandler, self).getData()

    @tornado.gen.coroutine
    def get(self):
        dat = yield self.get_data(**self.psp_kwargs)
        self.write(dat)
