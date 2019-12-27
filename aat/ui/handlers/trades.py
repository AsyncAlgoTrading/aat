import tornado.gen
from .base import HTTPHandler
from tornado.concurrent import run_on_executor
from perspective import PerspectiveHTTPMixin
from aat.enums import PairType
from aat.structs import Instrument


class TradesHandler(PerspectiveHTTPMixin, HTTPHandler):
    '''Server Handler
    Extends:
        HTTPHandler
    '''

    def initialize(self, trading_engine, psp_kwargs=None):
        self.te = trading_engine
        self.psp_kwargs = psp_kwargs or {}

    @run_on_executor
    def get_data(self, exchange=None, pair=None, **psp_kwargs):
        try:
            if pair is not None:
                pair = PairType.from_string(pair)
                instrument = Instrument(underlying=pair)
            else:
                instrument = None
        except (ValueError, TypeError):
            instrument = None

        msgs = [x.to_dict(True, True) for x in self.te.query.query_trades(instrument)]
        if len(msgs) > 0:
            for msg in msgs:
                msg['underlying'] = msg['instrument']['underlying']
                msg['instrument'] = msg['instrument']['underlying'] + ',' + msg['instrument']['type']

        super(TradesHandler, self).loadData(data=msgs, **psp_kwargs)
        return super(TradesHandler, self).getData()

    @tornado.gen.coroutine
    def get(self):
        pair = self.get_argument('pair', '')
        dat = yield self.get_data(pair=pair, **self.psp_kwargs)
        self.write(dat)
