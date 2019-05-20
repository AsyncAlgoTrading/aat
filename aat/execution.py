from .config import ExecutionConfig
from .exchange import Exchange
from .enums import Side
from .structs import TradeRequest, TradeResponse
from .logging import EXEC as exlog


class Execution(object):
    def __init__(self, options: ExecutionConfig, exchange: Exchange) -> None:
        self.trading_type = options.trading_type

        self._ex = exchange
        self._exs = []

    def requestBuy(self, req: TradeRequest) -> TradeResponse:
        resp = self._ex.buy(req)
        exlog.info('Order info: %s' % resp)
        return resp

    def requestSell(self, req: TradeRequest) -> TradeResponse:
        resp = self._ex.sell(req)
        exlog.info('Order info: %s' % resp)
        return resp

    def request(self, req: TradeRequest) -> TradeResponse:
        if req.side == Side.BUY:
            return self.requestBuy(req)
        return self.requestSell(req)

    def cancel(self, resp: TradeResponse):  # TODO
        return self._ex.cancel(resp)

    def cancelAll(self):
        return self._ex.cancelAll()
