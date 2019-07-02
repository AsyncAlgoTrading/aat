from abc import ABCMeta, abstractmethod
from .callback import Callback
from .structs import TradeRequest, TradeResponse


class Strategy(metaclass=ABCMeta):
    '''Strategy interface'''
    def __init__(self, query=None, exchanges=None, *args, **kwargs) -> None:
        self.query = query
        self.exchanges = exchanges

    def setEngine(self, engine) -> None:
        self._te = engine

    @abstractmethod
    def request(self, req: TradeRequest):
        '''request'''


class TradingStrategy(Strategy, Callback):
    def request(self, req: TradeRequest) -> None:
        '''attempt to buy/sell'''
        return self._te.request(req, self)

    def cancel(self, resp: TradeResponse) -> None:
        '''cancel order'''
        return self._te.cancel(resp, self)

    def cancelAll(self):
        '''cancel all orders'''
        return self._te.cancelAll(self)

    def slippage(self, data: TradeResponse) -> TradeResponse:
        '''slippage model. default is pass through'''
        return data

    def transactionCost(self, data: TradeResponse) -> TradeResponse:
        '''txns cost model. default is pass through'''
        return data

    def to_dict(self, *args):
        return {'name': self.__class__.__name__}
