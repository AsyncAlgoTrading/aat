from abc import ABCMeta, abstractmethod
from .callback import Callback
from .structs import TradeRequest, TradeResponse
from .enums import TickType


class DataSource(metaclass=ABCMeta):
    pass


class RestAPIDataSource(DataSource):
    @abstractmethod
    def accounts(self):
        '''get account information'''

    @abstractmethod
    def buy(self, req: TradeRequest) -> TradeResponse:
        '''execute a buy order'''

    @abstractmethod
    def sell(self, req: TradeRequest) -> TradeResponse:
        '''execute a sell order'''

    @abstractmethod
    def cancel(self, resp: TradeResponse) -> None:
        '''cancel an order'''

    @abstractmethod
    def cancelAll(self) -> None:
        '''cancel all orders'''

    @abstractmethod
    def orderBook(self):
        '''return the order book'''

    @abstractmethod
    def historical(self, timeframe='1m', since=None, limit=None):
        '''get historical data (for backtesting)'''


class StreamingDataSource(DataSource):
    def __init__(self, *args, **kwargs) -> None:
        self._running = False
        self._callbacks = {TickType.TRADE: [],
                           TickType.RECEIVED: [],
                           TickType.ERROR: [],
                           TickType.OPEN: [],
                           TickType.DONE: [],
                           TickType.CHANGE: [],
                           TickType.ANALYZE: [],
                           TickType.HALT: [],
                           TickType.CONTINUE: []}

    @abstractmethod
    async def run(self, engine) -> None:
        '''run the exchange'''

    @abstractmethod
    async def close(self) -> None:
        '''close the websocket'''

    @abstractmethod
    def seqnum(self, number: int):
        '''manage sequence numbers'''

    @abstractmethod
    def receive(self):
        '''receive data and call callbacks'''

    def callback(self, field: str, data) -> None:
        for cb in self._callbacks[field]:
            cb(data)

    # Data functions
    @abstractmethod
    def tickToData(self, jsn):
        '''convert json to market data based on fields'''

    def onTrade(self, callback: Callback) -> None:
        self._callbacks[TickType.TRADE].append(callback)

    def onReceived(self, callback: Callback) -> None:
        self._callbacks[TickType.RECEIVED].append(callback)

    def onOpen(self, callback: Callback) -> None:
        self._callbacks[TickType.OPEN].append(callback)

    def onDone(self, callback: Callback) -> None:
        self._callbacks[TickType.DONE].append(callback)

    def onChange(self, callback: Callback) -> None:
        self._callbacks[TickType.CHANGE].append(callback)

    def onError(self, callback: Callback) -> None:
        self._callbacks[TickType.ERROR].append(callback)

    def onExit(self, callback: Callback) -> None:
        self._callbacks[TickType.EXIT].append(callback)

    def onAnalyze(self, callback: Callback) -> None:
        self._callbacks[TickType.ANALYZE].append(callback)

    def onHalt(self, callback: Callback) -> None:
        self._callbacks[TickType.HALT].append(callback)

    def onContinue(self, callback: Callback) -> None:
        self._callbacks[TickType.CONTINUE].append(callback)

    def registerCallback(self, callback: Callback) -> None:
        if not isinstance(callback, Callback):
            raise Exception('%s is not an instance of class '
                            'Callback' % callback)

        if callback.onTrade:
            self.onTrade(callback.onTrade)
        if callback.onReceived:
            self.onReceived(callback.onReceived)
        if callback.onOpen:
            self.onOpen(callback.onOpen)
        if callback.onDone:
            self.onDone(callback.onDone)
        if callback.onChange:
            self.onChange(callback.onChange)
        if callback.onError:
            self.onError(callback.onError)
        if callback.onAnalyze:
            self.onAnalyze(callback.onAnalyze)
        if callback.onHalt:
            self.onHalt(callback.onHalt)
        if callback.onContinue:
            self.onContinue(callback.onContinue)
