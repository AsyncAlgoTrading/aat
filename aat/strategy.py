from typing import Callable
from abc import ABCMeta, abstractmethod
from .callback import Callback
from .structs import MarketData, TradeRequest, TradeResponse


class Strategy(metaclass=ABCMeta):
    '''Strategy interface'''
    def __init__(self, *args, **kwargs) -> None:
        self._actions = []
        self._requests = []

    def setEngine(self, engine) -> None:
        self._te = engine

    @abstractmethod
    def requestBuy(self,
                   callback: Callback,
                   data: MarketData):
        '''requestBuy'''

    @abstractmethod
    def requestSell(self,
                    callback: Callback,
                    data: MarketData):
        '''requestSell'''

    def registerAction(self, time, actionType, data) -> None:
        '''add action to log'''
        self._actions.append((time, actionType, data))

    def registerDesire(self, time, actionType, data) -> None:
        '''add action to log'''
        self._requests.append((time, actionType, data))


class TradingStrategy(Strategy, Callback):
    def requestBuy(self, callback: Callable, req: TradeRequest, callback_failure=None) -> None:
        '''attempt to buy'''
        self._te.requestBuy(callback, req, callback_failure, self)

    def requestSell(self, callback: Callable, req: TradeRequest, callback_failure=None) -> None:
        '''attempt to sell'''
        self._te.requestSell(callback, req, callback_failure, self)

    def cancel(self, callback: Callable, resp: TradeResponse, callback_failure=None) -> None:
        '''cancel order'''
        self._te.cancel(callback, resp, callback_failure, self)

    def cancelAll(self, callback: Callable, callback_failure=None):
        '''cancel all orders'''
        self._te.cancelAll(callback, callback_failure, self)

    def slippage(self, data: TradeResponse) -> TradeResponse:
        '''slippage model. default is pass through'''
        return data

    def transactionCost(self, data: TradeResponse) -> TradeResponse:
        '''txns cost model. default is pass through'''
        return data
