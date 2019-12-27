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
from .handlers.accounts import AccountsHandler
from .handlers.exchanges import ExchangesHandler
from .handlers.instruments import InstrumentsHandler
from .handlers.last_price import LastPriceHandler
from .handlers.login import LoginHandler, LogoutHandler
from .handlers.strategies import StrategiesHandler
from .handlers.strategy_trade_request import StrategyTradeRequestHandler
from .handlers.strategy_trade_response import StrategyTradeResponseHandler
from .handlers.trades import TradesHandler
from .handlers.html import HTMLHandler, HTMLOpenHandler
from ..logging import log


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

        if not cookie_secret:
            nonce = int(time.time() * 1000)
            encoded_payload = ujson.dumps({"nonce": nonce}).encode()
            b64 = base64.b64encode(encoded_payload)
            cookie_secret = hmac.new(str(uuid.uuid1()).encode(), b64, hashlib.sha384).hexdigest()

        login_code = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(20))
        log.critical(f'\n**********\nLogin code: {login_code}\n**********')

        settings = {
            "cookie_secret": cookie_secret,
            "login_url": "/login",
            "login_code": login_code,
            "debug": debug,
            "template_path": os.path.join(root, 'templates'),
        }
        settings.update(custom_settings or {})
        extra_handlers = extra_handlers or []
        for route, handler, h_kwargs in extra_handlers:
            if 'trading_engine' in h_kwargs:
                h_kwargs['trading_engine'] = trading_engine

        super(ServerApplication, self).__init__(
            extra_handlers + [
                (r"/api/v1/json/accounts", AccountsHandler, {'trading_engine': trading_engine, 'psp_kwargs': {'index': 'id'}}),
                (r"/api/v1/arrow/accounts", AccountsHandler, {'trading_engine': trading_engine, 'psp_kwargs': {'index': 'id', 'transfer_as_arrow': True}}),
                (r"/api/v1/json/exchanges", ExchangesHandler, {'trading_engine': trading_engine, 'psp_kwargs': {'index': 'id'}}),
                (r"/api/v1/arrow/exchanges", ExchangesHandler, {'trading_engine': trading_engine, 'psp_kwargs': {'index': 'id', 'transfer_as_arrow': True}}),
                (r"/api/v1/json/instruments", InstrumentsHandler, {'trading_engine': trading_engine, 'psp_kwargs': {'index': 'underlying'}}),
                (r"/api/v1/arrow/instruments", InstrumentsHandler, {'trading_engine': trading_engine, 'psp_kwargs': {'index': 'underlying', 'transfer_as_arrow': True}}),
                (r"/api/v1/json/strategies", StrategiesHandler, {'trading_engine': trading_engine,
                                                                 'psp_kwargs': {'view': 'hypergrid'}}),
                (r"/api/v1/arrow/strategies", StrategiesHandler, {'trading_engine': trading_engine,
                                                                  'psp_kwargs': {'view': 'hypergrid', 'transfer_as_arrow': True}}),
                (r"/api/v1/json/strategy-trade-requests", StrategyTradeRequestHandler, {'trading_engine': trading_engine,
                                                                                        'psp_kwargs': {'index': 'time', 'view': 'hypergrid'}}),
                (r"/api/v1/arrow/strategy-trade-requests", StrategyTradeRequestHandler, {'trading_engine': trading_engine,
                                                                                         'psp_kwargs': {'index': 'time', 'view': 'hypergrid', 'transfer_as_arrow': True}}),
                (r"/api/v1/json/strategy-trade-responses", StrategyTradeResponseHandler, {'trading_engine': trading_engine,
                                                                                          'psp_kwargs': {'index': 'time', 'view': 'hypergrid'}}),
                (r"/api/v1/arrow/strategy-trade-responses", StrategyTradeResponseHandler, {'trading_engine': trading_engine,
                                                                                           'psp_kwargs': {'index': 'time', 'view': 'hypergrid', 'transfer_as_arrow': True}}),
                (r"/api/v1/json/last-price-all", LastPriceHandler, {'trading_engine': trading_engine,
                                                                    'psp_kwargs': {'index': 'instrument', 'view': 'hypergrid'}}),
                (r"/api/v1/arrow/last-price-all", LastPriceHandler, {'trading_engine': trading_engine,
                                                                     'psp_kwargs': {'index': 'instrument', 'view': 'hypergrid', 'transfer_as_arrow': True}}),
                (r"/api/v1/json/trades", TradesHandler, {'trading_engine': trading_engine,
                                                         'psp_kwargs': {'index': 'time', 'view': 'hypergrid', 'limit': 100}}),
                (r"/api/v1/arrow/trades", TradesHandler, {'trading_engine': trading_engine,
                                                          'psp_kwargs': {'index': 'time', 'view': 'hypergrid', 'limit': 100, 'transfer_as_arrow': True}}),
                (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": static}),
                (r"/api/v1/login", LoginHandler, {}),
                (r"/api/v1/logout", LogoutHandler, {}),
                (r"/login", HTMLOpenHandler, {'template': '404.html'}),
                (r"/logout", HTMLHandler, {'template': '404.html'}),
                (r"/(.*)", HTMLOpenHandler, {'template': '404.html'})
            ], **settings)
