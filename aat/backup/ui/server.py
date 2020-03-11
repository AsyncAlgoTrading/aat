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

    # Perspectives
    manager = PerspectiveManager()

    # Accounts
    accounts = Table([a.to_dict(True) for ex in trading_engine.exchanges.values() for a in ex.accounts().values()])
    manager.host_table("accounts", accounts)

    cookie_secret = generate_cookie_secret() if not cookie_secret else cookie_secret

    handlers = (extra_handlers or []) + [
        (r"/api/v1/ws", PerspectiveTornadoHandler, {"manager": manager, "check_origin": True}),
    ]

    context = {}

    return make_application(
        port=port,
        debug=debug,
        assets_dir=root,
        static_dir=static,
        cookie_secret=cookie_secret,
        basepath=basepath,
        apipath=apipath,
        wspath=wspath,
        sqlalchemy_sessionmaker=sessionmaker,
        UserSQLClass=User,
        APIKeySQLClass=APIKey,
        user_id_field='id',
        apikey_id_field='id',
        user_apikeys_field='apikeys',
        apikey_user_field='user',
        user_admin_field='admin',
        user_admin_value=True,
        extra_handlers=handlers,
        extra_context=context,
    )
