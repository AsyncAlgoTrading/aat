import tornado.web
import tornado.websocket
from perspective import PerspectiveHTTPMixin
from aat.enums import PairType
from aat.structs import Instrument


class ServerTradesMixin(PerspectiveHTTPMixin):
    def get_data(self, exchange=None, pair=None, **psp_kwargs):
        try:
            if pair is not None:
                pair = PairType.from_string(pair)
                instrument = Instrument(underlying=pair)
            else:
                instrument = None
        except (ValueError, TypeError):
            instrument = None

        msgs = [x.to_dict(True, True) for x in self.te.query().query_trades(instrument)]
        if len(msgs) > 0:
            for msg in msgs:
                msg['underlying'] = msg['instrument']['underlying']
                msg['instrument'] = msg['instrument']['underlying'] + ',' + msg['instrument']['type']

        psp_kwargs['data'] = msgs
        super(ServerTradesMixin, self).loadData(**psp_kwargs)
        return super(ServerTradesMixin, self).getData()


class ServerTradesHandler(ServerTradesMixin, tornado.web.RequestHandler):
    '''Server Handler
    Extends:
        tornado.web.RequestHandler
    '''
    def initialize(self, trading_engine, psp_kwargs):
        self.te = trading_engine
        self.psp_kwargs = psp_kwargs

    def get(self):
        pair = self.get_argument('pair', '')
        self.write(self.get_data(pair=pair, **self.psp_kwargs))
