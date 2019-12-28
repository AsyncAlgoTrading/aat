import os
import os.path
import logging
import secrets
import string
import time
import tornado.ioloop
import tornado.web
import ujson
import uuid
from perspective import Table, PerspectiveManager, PerspectiveTornadoHandler
from .handlers.login import LoginHandler, LogoutHandler
from .handlers.html import HTMLHandler, HTMLOpenHandler
from ..utils import generate_cookie_secret
from ..logging import log


class ServerApplication(tornado.web.Application):
    def __init__(self,
                 trading_engine,
                 port='8080',
                 extra_handlers=None,
                 custom_settings=None,
                 debug=True,
                 cookie_secret=None,
                 *args,
                 **kwargs):
        root = os.path.join(os.path.dirname(__file__), 'assets')
        static = os.path.join(root, 'static')

        logging.getLogger('tornado.access').disabled = False

        # Perspectives
        manager = PerspectiveManager()

        # Accounts
        accounts = Table([a.to_dict(True) for ex in trading_engine.exchanges.values() for a in ex.accounts().values()])
        manager.host_table("accounts", accounts)

        cookie_secret = generate_cookie_secret() if not cookie_secret else cookie_secret
        login_code = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(20))
        log.critical(f'\n**********\nLogin code: {login_code}\n**********')

        settings = {
            "cookie_secret": cookie_secret,
            "login_url": "/login",
            "login_code": login_code,
            "debug": debug,
            "template_path": os.path.join(root, 'templates'),
        }

        context = {
            'basepath': '/',
            'wspath': 'ws:0.0.0.0:{}/'.format(port),
        }

        settings.update(custom_settings or {})

        extra_handlers = extra_handlers or []
        for _, handler, h_kwargs in extra_handlers:
            if 'trading_engine' in h_kwargs:
                h_kwargs['trading_engine'] = trading_engine
            if issubclass(handler, HTMLHandler) or issubclass(handler, HTMLOpenHandler):
                h_kwargs['context'] = context

        super(ServerApplication, self).__init__(
            extra_handlers + [
                (r"/api/v1/ws", PerspectiveTornadoHandler, {"manager": manager, "check_origin": True}),
                (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": static}),
                (r"/api/v1/login", LoginHandler, {}),
                (r"/api/v1/logout", LogoutHandler, {}),
                (r"/login", HTMLOpenHandler, {'template': '404.html', 'context': context}),
                (r"/logout", HTMLHandler, {'template': '404.html', 'context': context}),
                (r"/(.*)", HTMLOpenHandler, {'template': '404.html', 'context': context})
            ], **settings)
