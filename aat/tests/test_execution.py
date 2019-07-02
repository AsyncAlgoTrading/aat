from mock import patch, MagicMock
from datetime import datetime


class TestExecution:
    def setup(self):
        pass
        # setup() before each test method

    def teardown(self):
        pass
        # teardown() after each test method

    @classmethod
    def setup_class(cls):
        pass
        # setup_class() before any methods in this class

    @classmethod
    def teardown_class(cls):
        pass
        # teardown_class() after any methods in this class

    def test_init(self):
        from ..execution import Execution
        from ..config import ExecutionConfig

        ex = MagicMock()

        ec = ExecutionConfig()
        e = Execution(ec, ex, MagicMock())
        assert e

    def test_request(self):
        from ..execution import Execution
        from ..enums import Side, PairType, OrderType, ExchangeType, CurrencyType
        from ..config import ExecutionConfig
        from ..structs import TradeRequest, Instrument, Account

        ex = {ExchangeType.COINBASE: MagicMock()}
        accounts = {CurrencyType.BTC: Account(id='1',
                                              currency=CurrencyType.BTC,
                                              balance=1.0,
                                              exchange=MagicMock(),
                                              value=-1,
                                              asOf=datetime.now()),
                    CurrencyType.USD: Account(id='2',
                                              currency=CurrencyType.USD,
                                              balance=1.0,
                                              exchange=MagicMock(),
                                              value=-1,
                                              asOf=datetime.now())}
        ex[ExchangeType.COINBASE].accounts.return_value = accounts
        ex[ExchangeType.COINBASE].buy.return_value.exchange = ExchangeType.COINBASE
        ec = ExecutionConfig()
        e = Execution(ec, ex, accounts)

        req = TradeRequest(side=Side.BUY,
                           instrument=Instrument(underlying=PairType.BTCUSD),
                           order_type=OrderType.MARKET,
                           exchange=ExchangeType.COINBASE,
                           volume=1.0,
                           price=1.0,
                           time=datetime.now())

        resp = e.request(req)

        req = TradeRequest(side=Side.SELL,
                           instrument=Instrument(underlying=PairType.BTCUSD),
                           order_type=OrderType.MARKET,
                           exchange=ExchangeType.COINBASE,
                           volume=1.0,
                           price=1.0,
                           time=datetime.now())

        resp = e.request(req)

        req = TradeRequest(side=Side.BUY,
                           instrument=Instrument(underlying=PairType.BTCUSD),
                           order_type=OrderType.MARKET,
                           exchange=ExchangeType.COINBASE,
                           volume=1.0,
                           price=1.0,
                           time=datetime.now())

        resp = e.request(req)
        e.cancel(resp)
        e.cancelAll()
