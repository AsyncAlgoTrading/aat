import aiohttp
import json
from functools import lru_cache
from .config import ExchangeConfig
from .enums import TickType, ExchangeType
from .order_entry import OrderEntry
from .market_data import MarketData


class Exchange(MarketData, OrderEntry):
    def __init__(self, exchange_type: ExchangeType, options: ExchangeConfig) -> None:
        super(Exchange, self).__init__()
        self._options = options
        self._exchange = exchange_type
        self._pending_orders = {}
        self._messages = {}
        self._messages_all = []

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

        if self._seqnum_enabled and res.type != TickType.HEARTBEAT:
            self.seqnum(res.sequence)

        if not self._running:
            pass

        if res.type != TickType.HEARTBEAT:
            if res.type not in self._messages:
                self._messages[res.type] = [res]
            else:
                self._messages[res.type].append(res)
            self._messages_all.append(res)

        if res.type == TickType.TRADE:
            self.callback(TickType.TRADE, res)
        elif res.type == TickType.RECEIVED:
            self.callback(TickType.RECEIVED, res)
        elif res.type == TickType.OPEN:
            self.callback(TickType.OPEN, res)
        elif res.type == TickType.DONE:
            self.callback(TickType.DONE, res)
        elif res.type == TickType.CHANGE:
            self.callback(TickType.CHANGE, res)
        elif res.type == TickType.HEARTBEAT:
            # TODO anything?
            pass
        else:
            self.callback(TickType.ERROR, res)

    def messages(self, by_type=False, instrument=None) -> list:
        if by_type:
            if instrument:
                return {x: [y for y in self._messages[x] if y.instrument == instrument] for x in self._messages}
            return self._messages
        if instrument:
            return [x for x in self._messages_all if x.instrument == instrument]
        return self._messages_all
