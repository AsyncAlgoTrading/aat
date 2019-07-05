from mock import MagicMock
from datetime import datetime


class TestRisk:
    def setup(self):
        from ..config import RiskConfig
        from ..risk import Risk
        from ..enums import ExchangeType, CurrencyType
        from ..structs import Account

        rc = RiskConfig()
        rc.max_risk = 100.0
        rc.max_drawdown = 100.0
        rc.total_funds = 100.0

        ex = {ExchangeType.COINBASE: MagicMock()}
        accounts = {CurrencyType.BTC: {ExchangeType.COINBASE: Account(id='1',
                                                                      currency=CurrencyType.BTC,
                                                                      balance=1.0,
                                                                      exchange=MagicMock(),
                                                                      value=-1,
                                                                      asOf=datetime.now())},
                    CurrencyType.USD: {ExchangeType.COINBASE: Account(id='2',
                                                                      currency=CurrencyType.USD,
                                                                      balance=1.0,
                                                                      exchange=MagicMock(),
                                                                      value=-1,
                                                                      asOf=datetime.now())}}
        ex[ExchangeType.COINBASE].accounts.return_value = accounts

        self.risk = Risk(rc, ex, accounts)

        # setup() before each test method

    def test_construct_reponse(self):
        pass

    def test_request(self):
        from ..structs import TradeRequest, Instrument
        from ..enums import Side, PairType, OrderType, ExchangeType

        req = TradeRequest(side=Side.BUY, instrument=Instrument(underlying=PairType.BTCUSD), order_type=OrderType.MARKET, volume=100.0, price=1.0, exchange=ExchangeType.COINBASE, time=datetime.now())
        resp = self.risk.request(req)
        resp = self.risk.requestBuy(req)

        # FIXME
        # assert resp.risk_check == True
        # assert resp.volume == 100.0
        # assert self.risk.outstanding == 0.0
        # assert self.risk.max_running_outstanding == 0.0
        # print(self.risk.max_running_outstanding_incr)
        # assert self.risk.max_running_outstanding_incr == []

        # req = TradeRequest(side=Side.BUY, volume=100.0, price=1.0)
        # resp = self.risk.request(req)

        # assert resp.risk_check == True

    def test_request2(self):
        from ..structs import TradeRequest, Instrument
        from ..enums import Side, PairType, OrderType, ExchangeType

        req = TradeRequest(side=Side.SELL, instrument=Instrument(underlying=PairType.BTCUSD), order_type=OrderType.MARKET, volume=50.0, price=1.0, exchange=ExchangeType.COINBASE, time=datetime.now())
        resp = self.risk.request(req)
        resp = self.risk.requestSell(req)

        # FIXME
        # assert resp.risk_check == True
        # assert resp.volume == 50.0
        # assert self.risk.outstanding == 50.0
        # assert self.risk.max_running_outstanding == 50.0
        # assert self.risk.max_running_outstanding_incr == [50.0]

        # req = TradeRequest(side=Side.BUY, volume=100.0, price=1.0)
        # resp = self.risk.request(req)

        # assert resp.risk_check == True
        # assert resp.volume == 50.0
        # assert self.risk.outstanding == 100.0
        # assert self.risk.max_running_outstanding == 100.0
        # assert self.risk.max_running_outstanding_incr == [50.0, 100.0]

        # req = TradeRequest(side=Side.BUY, volume=100.0, price=1.0)
        # resp = self.risk.request(req)

        # assert resp.risk_check == False

    def test_update(self):
        from ..structs import TradeRequest, TradeResponse, Instrument
        from ..enums import Side, PairType, OrderType, ExchangeType, TradeResult
        req = TradeRequest(side=Side.SELL, instrument=Instrument(underlying=PairType.BTCUSD), order_type=OrderType.MARKET, volume=50.0, price=1.0, exchange=ExchangeType.COINBASE, time=datetime.now())
        resp = TradeResponse(side=Side.SELL, instrument=Instrument(underlying=PairType.BTCUSD), request=req, order_id='1', volume=50.0, price=1.0, exchange=ExchangeType.COINBASE, time=datetime.now(), status=TradeResult.FILLED)
        self.risk.update(resp)
        assert self.risk.outstanding == -50

    def test_cancel(self):
        from ..structs import TradeRequest, TradeResponse, Instrument
        from ..enums import Side, PairType, OrderType, ExchangeType, TradeResult
        req = TradeRequest(side=Side.SELL, instrument=Instrument(underlying=PairType.BTCUSD), order_type=OrderType.MARKET, volume=50.0, price=1.0, exchange=ExchangeType.COINBASE, time=datetime.now())
        resp = TradeResponse(side=Side.SELL, instrument=Instrument(underlying=PairType.BTCUSD), request=req, order_id='1', volume=50.0, price=1.0, exchange=ExchangeType.COINBASE, time=datetime.now(), status=TradeResult.FILLED)
        self.risk.cancel(resp)
        assert self.risk.outstanding == 50
