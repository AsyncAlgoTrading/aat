import ccxt
import json
from datetime import datetime
from functools import lru_cache
from typing import List
from ..config import SyntheticExchangeConfig
from ..enums import ExchangeType, TickType, PairType, OrderType, CurrencyType
from ..exchange import Exchange
from ..order_book import OrderBook
from ..structs import MarketData, TradeRequest, TradeResponse, Instrument, Account


class SyntheticExchange(Exchange):
    def __init__(self,
                 exchange_type: ExchangeType,
                 options: SyntheticExchangeConfig,
                 query_engine=None) -> None:
        super(SyntheticExchange, self).__init__(exchange_type=exchange_type, options=options, query_engine=query_engine)
        self._book = OrderBook(options.instruments)
        self._underlying_exchange = options.exchange_type
        self._advesaries = []

    def generateMsg(self):
        raise NotImplementedError()

    async def receive(self) -> None:
        async for msg in self.generateMsg():
            self.callback_data(json.loads(msg.data))

    @lru_cache(None)
    def oe_client(self):
        return ccxt.coinbasepro({'enableRateLimit': True})

    async def close(self) -> None:
        '''close the websocket'''
        pass

    @lru_cache(None)
    def accounts(self):
        all_curs = set()
        for inst in self._options.instruments:
            all_curs.add(inst.underlying.value[0])
            all_curs.add(inst.underlying.value[1])

        return [Account(id=str(cur.value),
                        currency=cur,
                        balance=100,
                        exchange=self.exchange(),
                        value=-1,
                        asOf=datetime.now()) for cur in all_curs]

    @lru_cache(None)
    def currencies(self) -> List[CurrencyType]:
        return [CurrencyType(x) for x in self.oe_client().fetch_curencies()]

    @lru_cache(None)
    def markets(self) -> List[Instrument]:
        return [Instrument(underlying=PairType.from_string(m['symbol'])) for m in self.oe_client().fetch_markets()]

    def orderBook(self, level=1):
        '''get order book'''
        raise NotImplementedError()

    def buy(self, req: TradeRequest) -> TradeResponse:
        '''execute a buy order'''
        for ad in self._advesaries:
            req = ad.beforeOrder(req)

        raise NotImplementedError()

        for ad in self._advesaries:
            req = ad.afterOrder(req)

    def sell(self, req: TradeRequest) -> TradeResponse:
        '''execute a sell order'''
        for ad in self._advesaries:
            req = ad.beforeOrder(req)

        raise NotImplementedError()

        for ad in self._advesaries:
            req = ad.afterOrder(req)

    def cancel(self, resp: TradeResponse):
        for ad in self._advesaries:
            resp = ad.beforeOrder(resp)

        raise NotImplementedError()

        for ad in self._advesaries:
            resp = ad.afterOrder(resp)

    def cancelAll(self, resp: TradeResponse):
        pass

    @lru_cache(None)
    def subscription(self):
        return []

    @lru_cache(None)
    def heartbeat(self):
        return []

    def tickToData(self, jsn: dict) -> MarketData:
        pass

    def strToTradeType(self, s: str, reason: str = '') -> TickType:
        pass

    def tradeReqToParams(self, req) -> dict:
        pass

    def currencyPairToString(self, cur: PairType) -> str:
        pass

    def orderTypeToString(self, typ: OrderType) -> str:
        pass

    def reasonToTradeType(self, s: str) -> TickType:
        pass


class Adversary(object):
    def __init__(self):
        pass

    def beforeData(self, data: MarketData, orig: MarketData) -> MarketData:
        pass

    def afterData(self, market) -> None:
        pass

    def beforeOrder(self, data: TradeRequest, market) -> None:
        pass

    def afterOrder(self, data: TradeResponse, market) -> None:
        pass
