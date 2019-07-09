from typing import List
from .config import ExecutionConfig
from .enums import Side, TradingType, TradeResult
from .exchange import Exchange
from .logging import log
from .structs import TradeRequest, TradeResponse, Account


class Execution(object):
    def __init__(self, options: ExecutionConfig, exchanges: List[Exchange], accounts: List[Account]) -> None:
        self.trading_type = options.trading_type
        self.exchanges = exchanges
        self.accounts = accounts
        self._backtest_id = 1

    def insufficientFunds(self, req):
        resp = TradeResponse(request=req,
                             side=req.side,
                             exchange=req.exchange,
                             volume=0.0,
                             price=0.0,
                             instrument=req.instrument,
                             status=TradeResult.REJECTED,
                             time=req.time,
                             strategy=req.strategy,
                             order_id='')
        return resp

    def backtest(self, req):
        resp = TradeResponse(request=req,
                             side=req.side,
                             exchange=req.exchange,
                             volume=req.volume,
                             price=req.price,
                             instrument=req.instrument,
                             status=TradeResult.FILLED,
                             time=req.time,
                             strategy=req.strategy,
                             order_id=str(self._backtest_id))
        self._backtest_id += 1
        return resp

    def simulation(self, req):
        resp = TradeResponse(request=req,
                             side=req.side,
                             exchange=req.exchange,
                             volume=req.volume,
                             price=req.price,
                             instrument=req.instrument,
                             status=TradeResult.FILLED,
                             time=req.time,
                             strategy=req.strategy,
                             order_id=str(self._backtest_id))
        self._backtest_id += 1
        return resp

    def requestBuy(self, req: TradeRequest) -> TradeResponse:
        # can afford?
        balance = self.exchanges[req.exchange].accounts()[req.instrument.underlying.value[1]].balance

        if balance < req.volume * req.price:
            return self.insufficientFunds(req)

        if self.trading_type == TradingType.BACKTEST:
            return self.backtest(req)
        if self.trading_type == TradingType.SIMULATION:
            return self.simulation(req)

        resp = self.exchanges[req.exchange].buy(req)
        log.info('Order info: %s' % resp)
        return resp

    def requestSell(self, req: TradeRequest) -> TradeResponse:
        # can afford?
        balance = self.exchanges[req.exchange].accounts()[req.instrument.underlying.value[0]].balance

        if balance < req.volume:
            return self.insufficientFunds(req)

        if self.trading_type == TradingType.BACKTEST:
            return self.backtest(req)
        if self.trading_type == TradingType.SIMULATION:
            return self.simulation(req)

        resp = self.exchanges[req.exchange].sell(req)
        log.info('Order info: %s' % resp)
        return resp

    def request(self, req: TradeRequest) -> TradeResponse:
        if req.side == Side.BUY:
            return self.requestBuy(req)
        return self.requestSell(req)

    def cancel(self, resp: TradeResponse):  # TODO
        return self.exchanges[resp.exchange].cancel(resp)

    def cancelAll(self):
        for ex in self.exchanges.values():
            ex.cancelAll()
