import tornado.web
import tornado.websocket


class ServerInstrumentsHandler(tornado.web.RequestHandler):
    '''Server Handler
    Extends:
        tornado.web.RequestHandler
    '''
    def initialize(self, trading_engine, **kwargs):
        self.te = trading_engine

    def get(self):
        msgs = [x.to_dict(True, True) for x in self.te.query().query_instruments()]
        self.write({'instruments': msgs})
