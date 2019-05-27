import aiohttp
import json
from functools import lru_cache
from .config import ExchangeConfig
from .enums import TickType, ExchangeType
from .order_entry import OrderEntry
from .market_data import MarketData


class Exchange(MarketData, OrderEntry):
    def __init__(self,
                 exchange_type: ExchangeType,
                 options: ExchangeConfig,
                 query_engine=None) -> None:
        super(Exchange, self).__init__()
        self._options = options
        self._exchange = exchange_type
        self._query_engine = query_engine

    @lru_cache(None)
    def options(self) -> ExchangeConfig:
        return self._options

    @lru_cache(None)
    def exchange(self) -> ExchangeType:
        return self._exchange

    async def receive(self) -> None:
        async for msg in self.ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                self.callback_data(json.loads(msg.data))
            elif msg.type == aiohttp.WSMsgType.ERROR:
                self.callback(TickType.ERROR, msg.data)

    def callback_data(self, data) -> None:
        res = self.tickToData(data)
        if res is None:
            return

        if self._seqnum_enabled and res.type != TickType.HEARTBEAT:
            self.seqnum(res.sequence)

        if not self._running:
            pass

        if res.type != TickType.HEARTBEAT:
            self.callback(res.type, res)
