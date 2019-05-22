import tornado.web
import tornado.websocket
import ujson
from perspective import PerspectiveHTTPMixin
from aat.enums import TickType, PairType
from aat.structs import Instrument


class ServerMessagesMixin(PerspectiveHTTPMixin):
    def get_data(self, type=None, exchange=None, page=1, pairtype=None, **psp_kwargs):
        try:
            type = TickType(type)
        except ValueError:
            type = None

        try:
            if pairtype is not None:
                pairtype = PairType.from_string(pairtype)
                instrument = Instrument(underlying=pairtype)
            else:
                instrument = None
        except (ValueError, TypeError):
            instrument = None

        if type is None:
            if instrument:
                msgs = [m for ex in self.te.exchanges().values() for m in ex.messages(False, instrument)[-(page+1)*20: -1 + (page)*20]] \
                    if page > 0 else \
                    [m for ex in self.te.exchanges().values() for m in ex.messages(False, instrument)]
            else:
                msgs = [m for ex in self.te.exchanges().values() for m in ex.messages()[-(page+1)*20: -1 + (page)*20]] \
                 if page > 0 else \
                 [m for ex in self.te.exchanges().values() for m in ex.messages()]
        else:
            if instrument:
                msgs = [m for ex in self.te.exchanges().values() for m in ex.messages(True, instrument).get(type, [])[page*20: (page+1)*20]] \
                 if page > 0 else \
                 [m for ex in self.te.exchanges().values() for m in ex.messages(True, instrument).get(type, [])]
            else:
                msgs = [m for ex in self.te.exchanges().values() for m in ex.messages(True).get(type, [])[page*20: (page+1)*20]] \
                 if page > 0 else \
                 [m for ex in self.te.exchanges().values() for m in ex.messages(True).get(type, [])]
        msgs = [x.to_dict(True, True) for x in msgs]

        if len(msgs) > 0:
            for msg in msgs:
                msg['underlying'] = msg['instrument']['underlying']
                msg['instrument'] = msg['instrument']['underlying'] + ',' + msg['instrument']['type']

        psp_kwargs['data'] = msgs
        super(ServerMessagesMixin, self).loadData(**psp_kwargs)
        return super(ServerMessagesMixin, self).getData()


class ServerMessagesHandler(ServerMessagesMixin, tornado.web.RequestHandler):
    '''Server Handler
    Extends:
        tornado.web.RequestHandler
    '''

    def initialize(self, trading_engine, psp_kwargs):
        self.te = trading_engine
        self.psp_kwargs = psp_kwargs

    def get(self):
        type = self.get_argument('type', None)
        page = int(self.get_argument('page', 1))
        pairtype = self.get_argument('pair', '')
        self.write(self.get_data(type=type, page=page, pairtype=pairtype, **self.psp_kwargs))


class ServerMessagesWSHandler(ServerMessagesMixin, tornado.web.RequestHandler):
    '''Server Handler
    Extends:
        tornado.web.RequestHandler
    '''

    def initialize(self, trading_engine):
        self.te = trading_engine

    def open(self):
        print('ws opened')

    def on_message(self, message):
        type = self.get_argument('type', None)
        page = int(self.get_argument('page', 1))
        pairtype = self.get_argument('pair', '')

        # TODO if page <0, stream
        msgs = self.get_data(type=type, page=page, pairtype=pairtype)
        self.write_message(ujson.dumps(msgs))

    def on_close(self):
        pass
