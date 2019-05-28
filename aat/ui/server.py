import os
import os.path
import logging
import tornado.ioloop
import tornado.web
from .handlers.accounts import AccountsHandler
from .handlers.exchanges import ExchangesHandler
from .handlers.instruments import InstrumentsHandler
from .handlers.strategies import StrategiesHandler
from .handlers.trades import TradesHandler
from .handlers.html import HTMLOpenHandler


class ServerApplication(tornado.web.Application):
    def __init__(self,
                 trading_engine,
                 extra_handlers=None,
                 custom_settings=None,
                 debug=True,
                 cookie_secret=None,
                 *args,
                 **kwargs):
        root = os.path.join(os.path.dirname(__file__), 'assets')
        static = os.path.join(root, 'static')

        logging.getLogger('tornado.access').disabled = False

        settings = {
                "cookie_secret": cookie_secret or "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",  # TODO
                "login_url": "/login",
                "debug": debug,
                "template_path": os.path.join(root, 'templates'),
                }
        settings.update(custom_settings or {})
        extra_handlers = extra_handlers or []
        for route, handler, h_kwargs in extra_handlers:
            if 'trading_engine' in h_kwargs:
                h_kwargs['trading_engine'] = trading_engine
        print(extra_handlers)

        super(ServerApplication, self).__init__(
          extra_handlers + [
            (r"/api/json/v1/accounts", AccountsHandler, {'trading_engine': trading_engine}),
            (r"/api/json/v1/exchanges", ExchangesHandler, {'trading_engine': trading_engine}),
            (r"/api/json/v1/instruments", InstrumentsHandler, {'trading_engine': trading_engine}),
            (r"/api/json/v1/strategies", StrategiesHandler, {'trading_engine': trading_engine,
                                                             'psp_kwargs': {'view': 'hypergrid'}}),
            (r"/api/json/v1/trades", TradesHandler, {'trading_engine': trading_engine,
                                                     'psp_kwargs': {'view': 'hypergrid', 'limit': 100}}),
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": static}),
            (r"/(.*)", HTMLOpenHandler, {'template': '404.html'})
          ], **settings)
