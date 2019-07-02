from typing import Callable
from abc import ABCMeta, abstractmethod
from .callback import Callback
from .structs import MarketData, TradeRequest, TradeResponse


class Strategy(metaclass=ABCMeta):
    '''Strategy interface'''
    def __init__(self, *args, **kwargs) -> None:
        pass

    def setEngine(self, engine) -> None:
        self._te = engine

    @abstractmethod
    def requestBuy(self, req: TradeRequest):
        '''requestBuy'''

    @abstractmethod
    def requestSell(self, req: TradeRequest):
        '''requestSell'''


class TradingStrategy(Strategy, Callback):
    def requestBuy(self, req: TradeRequest) -> None:
        '''attempt to buy'''
        return self._te.requestBuy(req, self)

    def requestSell(self, req: TradeRequest) -> None:
        '''attempt to sell'''
        return self._te.requestSell(req, self)

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
