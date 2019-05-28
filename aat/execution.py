from typing import List
from .config import ExecutionConfig
from .exchange import Exchange
from .enums import Side
from .structs import TradeRequest, TradeResponse
from .logging import EXEC as exlog


class Execution(object):
    def __init__(self, options: ExecutionConfig, exchanges: List[Exchange]) -> None:
        self.trading_type = options.trading_type
        self._exs = exchanges

    def requestBuy(self, req: TradeRequest) -> TradeResponse:
        resp = self._exs[req.exchange].buy(req)
        exlog.info('Order info: %s' % resp)
        return resp

    def requestSell(self, req: TradeRequest) -> TradeResponse:
        resp = self._exs[req.exchange].sell(req)
        exlog.info('Order info: %s' % resp)
        return resp

    def request(self, req: TradeRequest) -> TradeResponse:
        if req.side == Side.BUY:
            return self.requestBuy(req)
        return self.requestSell(req)

    def cancel(self, resp: TradeResponse):  # TODO
        return self._exs[resp.exchange].cancel(resp)

    def cancelAll(self):
        for ex in self._exs.values():
            ex.cancelAll()
