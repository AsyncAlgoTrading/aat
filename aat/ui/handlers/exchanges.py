import tornado.gen
from tornado.concurrent import run_on_executor
from perspective import PerspectiveHTTPMixin
from .base import HTTPHandler
from aat.enums import ExchangeType_to_string


class ExchangesHandler(PerspectiveHTTPMixin, HTTPHandler):
    '''Server Handler
    Extends:
        HTTPHandler
    '''

    def initialize(self, trading_engine, psp_kwargs=None):
        self.te = trading_engine
        self.psp_kwargs = psp_kwargs or {}

    @run_on_executor
    def get_data(self, **psp_kwargs):
        exchanges = self.te.query.query_exchanges()
        msgs = [{'id': j + i * len(exchanges),
                 'name': ExchangeType_to_string(x['exchange']),
                 'instrument': y.to_dict(True, True)['underlying']}
                for i, x in enumerate(exchanges)
                for j, y in enumerate(x['instruments'])
                ]
        super(ExchangesHandler, self).loadData(data=msgs, **psp_kwargs)
        return super(ExchangesHandler, self).getData()

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        dat = yield self.get_data(**self.psp_kwargs)
        self.write(dat)
