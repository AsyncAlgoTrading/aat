import tornado.web
from perspective import PerspectiveHTTPMixin


class ServerAccountsHandler(PerspectiveHTTPMixin, tornado.web.RequestHandler):
    '''Server Handler
    Extends:
        tornado.web.RequestHandler
    '''

    def initialize(self, trading_engine, **psp_kwargs):
        self.te = trading_engine
        self.psp_kwargs = psp_kwargs

    def get(self):
        try:
            self.psp_kwargs['data'] = [a.to_dict(True) for ex in self.te.exchanges().values() for a in ex.accounts()]
            self.loadData(**self.psp_kwargs)
            self.write(self.getData())
        except Exception as e:
            self.write(e)
