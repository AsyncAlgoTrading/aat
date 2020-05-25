import base64
import hashlib
import hmac
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
from tornado_sqlalchemy_login.handlers import LoginHandler, LogoutHandler, RegisterHandler, APIKeyHandler
from tornado_sqlalchemy_login import SQLAlchemyLoginManagerOptions, SQLAlchemyLoginManager
from ..persistence import User, APIKey
from ..utils import generate_cookie_secret
from ..logging import log


class ServerApplication(tornado.web.Application):
    def __init__(self,
                 trading_engine,
                 port,
                 extra_handlers=None,
                 custom_settings=None,
                 debug=True,
                 cookie_secret=None,
                 *args,
                 **kwargs):
        logging.getLogger('tornado.access').disabled = False

        basepath = "/"
        wspath = "/api/v1/ws"

        context = {'basepath': basepath,
                   'wspath': wspath}

        # SQLAlchemy Login Configuration
        sqlalchemy_login_config = SQLAlchemyLoginManagerOptions(
            port=port,
            UserClass=User,
            APIKeyClass=APIKey,
        )

        settings = {"cookie_secret": cookie_secret,
                    "login_url": basepath + "login",
                    "debug": debug}
        settings.update(custom_settings)

        extra_handlers = extra_handlers or []
        for route, handler, h_kwargs in extra_handlers:
            if 'trading_engine' in h_kwargs:
                h_kwargs['trading_engine'] = trading_engine

        default_handlers = [
            (r"/api/v1/login", LoginHandler, context),
            (r"/api/v1/logout", LogoutHandler, context),
            (r"/api/v1/register", RegisterHandler, context),
            (r"/api/v1/apikeys", APIKeyHandler, context),
            (r"/api/v1/ws", PerspectiveTornadoHandler, {"manager": trading_engine.perspective_manager, "check_origin": True}),
        ]

        for handler in extra_handlers:
            override = False
            for i, default in enumerate(default_handlers):
                if default[0] == handler[0]:
                    # override default handler
                    override = True
                    d = default[2]
                    d.update(handler[2])
                    default_handlers[i] = (handler[0], handler[1], d)
            if not override:
                default_handlers.append(handler)

        super(ServerApplication, self).__init__(default_handlers,
                                                login_manager=SQLAlchemyLoginManager(trading_engine.sessionmaker,
                                                                                     sqlalchemy_login_config),
                                                **settings)
