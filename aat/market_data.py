import aiohttp
from abc import abstractmethod
from .data_source import StreamingDataSource
from .define import EXCHANGE_MARKET_DATA_ENDPOINT
from .enums import OrderType, PairType, CurrencyType, TickType
from .structs import MarketData
from .logging import LOG as log


class MarketData(StreamingDataSource):
    def __init__(self, *args, **kwargs) -> None:
        super(MarketData, self).__init__()
        self._lastseqnum = -1
        self._missingseqnum = set()  # type: set
        self._seqnum_enabled = False

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
                str(x) for x in range(self._lastseqnum+1, number+1)))
            self._missingseqnum.update(
                x for x in range(self._lastseqnum+1, number+1))
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

    @abstractmethod
    def strToTradeType(self, s: str) -> TickType:
        pass

    @abstractmethod
    def tradeReqToParams(self, req) -> dict:
        pass

    def currencyToString(self, cur: CurrencyType) -> str:
        if cur == CurrencyType.BTC:
            return 'BTC'
        if cur == CurrencyType.ETH:
            return 'ETH'
        if cur == CurrencyType.LTC:
            return 'LTC'
        if cur == CurrencyType.BCH:
            return 'BCH'
        else:
            raise Exception('Pair not recognized: %s' % str(cur))

    @abstractmethod
    def currencyPairToString(self, cur: PairType) -> str:
        pass

    @abstractmethod
    def orderTypeToString(self, typ: OrderType) -> str:
        pass

    @abstractmethod
    def reasonToTradeType(self, s: str) -> TickType:
        pass
