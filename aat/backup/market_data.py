import aiohttp
from abc import abstractmethod
from .callback import Callback
from .data_source import StreamingDataSource
from .define import EXCHANGE_MARKET_DATA_ENDPOINT
from .enums import TickType
from .logging import log
from .structs import MarketData
from .utils import CallbackException


class MarketData(metaclass=ABCMeta):
    def __init__(self, *args, **kwargs) -> None:
        self._running = False
        self._callbacks = {TickType.TRADE: [],
                           TickType.ERROR: [],
                           TickType.OPEN: [],
                           TickType.FILL: [],
                           TickType.CANCEL: [],
                           TickType.CHANGE: [],
                           TickType.ANALYZE: [],
                           TickType.HALT: [],
                           TickType.CONTINUE: []}
        self._lastseqnum = -1
        self._missingseqnum = set()  # type: set
        self._seqnum_enabled = False

    @abstractmethod
    def receive(self):
        '''receive data and call callbacks'''

    def callback(self, field: str, data, *args, **kwargs) -> None:
        for cb in self._callbacks[field]:
            cb(data, *args, **kwargs)

    def onTrade(self, callback: Callback) -> None:
        self._callbacks[TickType.TRADE].append(callback)

    def onOpen(self, callback: Callback) -> None:
        self._callbacks[TickType.OPEN].append(callback)

    def onFill(self, callback: Callback) -> None:
        self._callbacks[TickType.FILL].append(callback)

    def onCancel(self, callback: Callback) -> None:
        self._callbacks[TickType.CANCEL].append(callback)

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
            raise CallbackException(f'{callback} is not an instance of class Callback')
        for att in ['onTrade',
                    'onOpen',
                    'onFill',
                    'onCancel',
                    'onChange',
                    'onError',
                    'onAnalyze',
                    'onHalt',
                    'onContinue']:
            if hasattr(callback, att):
                getattr(self, att)(getattr(callback, att))

    @abstractmethod
    def subscription(self):
        '''subscription for websocket'''

    @abstractmethod
    def heartbeat(self):
        '''heartbeat for websocket'''

    def seqnum(self, number: int) -> None:
        if self._lastseqnum == -1:
            # first seen
            self._lastseqnum = number
            return

        if number != self._lastseqnum + 1 and number not in self._missingseqnum:
            log.error('ERROR: Missing sequence number/s: %s' % ','.join(
                str(x) for x in range(self._lastseqnum + 1, number + 1)))
            self._missingseqnum.update(
                x for x in range(self._lastseqnum + 1, number + 1))
            log.error(self._missingseqnum)

        if number in self._missingseqnum:
            self._missingseqnum.remove(number)
            log.warning('INFO: Got out of order data for seqnum: %s' % number)

        else:
            self._lastseqnum = number

    async def close(self) -> None:
        '''close the websocket'''
        await self.ws.close()

    async def run(self, engine) -> None:
        options = self.options()
        session = aiohttp.ClientSession()

        while True:
            # startup and redundancy
            log.info('Starting....')
            self.ws = await session.ws_connect(EXCHANGE_MARKET_DATA_ENDPOINT(self.exchange(), options.trading_type))
            log.info(f'Connected: {self.exchange()}')

            for sub in self.subscription():
                await self.ws.send_str(sub)
                log.info('Sending Subscription %s' % sub)

            if self.heartbeat():
                await self.ws.send_str(self.heartbeat())
                log.info('Sending Heartbeat %s' % self.heartbeat())

            log.info('')
            log.critical(f'Starting algo trading: {self.exchange()}')
            try:
                while True:
                    await self.receive()

            except KeyboardInterrupt:
                log.critical('Terminating program')
                return

    @abstractmethod
    def tickToData(self, jsn: dict) -> MarketData:
        pass
