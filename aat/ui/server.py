import os
import os.path
import logging
import tornado.ioloop
import tornado.web
from .handlers.accounts import ServerAccountsHandler
from .handlers.messages import ServerMessagesHandler, ServerMessagesWSHandler
from .handlers.orders import ServerOrdersHandler
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
            (r"/api/json/v1/accounts", ServerAccountsHandler, {'trading_engine': trading_engine}),
            (r"/api/json/v1/orders", ServerOrdersHandler, {'trading_engine': trading_engine,
                                                           'psp_kwargs': {'view': 'hypergrid',
                                                                          'columns': ['time', 'volume', 'price', 'instrument'],
                                                                          'columnpivots': ['side'],
                                                                          'sort': ['price', 'asc'],
                                                                          'filters': ['reason', '==', 'ChangeReason.OPENED'],
                                                                          }}),
            (r"/api/json/v1/messages", ServerMessagesHandler, {'trading_engine': trading_engine,
                                                               'psp_kwargs': {'view': 'y_line',
                                                                              'aggregates': {'price': 'last'},
                                                                              'columns': 'price',
                                                                              'rowpivots': 'time',
                                                                              'columnpivots': ['type', 'side']}}),
            (r"/api/ws/v1/messages", ServerMessagesWSHandler, {'trading_engine': trading_engine}),
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": static}),
            (r"/(.*)", HTMLOpenHandler, {'template': '404.html'})
          ], **settings)
