import os
import os.path
import logging
import tornado.ioloop
import tornado.web
from .handlers.accounts import AccountsHandler
from .handlers.exchanges import ExchangesHandler
from .handlers.instruments import InstrumentsHandler
from .handlers.last_price import LastPriceHandler
from .handlers.strategies import StrategiesHandler
from .handlers.strategy_trade_request import StrategyTradeRequestHandler
from .handlers.strategy_trade_response import StrategyTradeResponseHandler
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
            (r"/(.*)", HTMLOpenHandler, {'template': '404.html'})
          ], **settings)
