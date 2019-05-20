import json
from functools import lru_cache
from ..config import ExchangeConfig
from ..enums import ExchangeType, OrderType, PairType, TickType
from ..exchange import Exchange
from ..structs import MarketData


class KrakenExchange(Exchange):
    def __init__(self, exchange_type: ExchangeType, options: ExchangeConfig) -> None:
        super(KrakenExchange, self).__init__(exchange_type, options)
        self._last = None
        self._orders = {}

    @lru_cache(None)
    def subscription(self):
        return [json.dumps({
            "event": "subscribe",
            "pair": [
                [self.currencyPairToString(x) for x in self.options().currency_pairs]
            ],
            "subscription": {
                "name": "ticker"
            }
        })]

    @lru_cache(None)
    def heartbeat(self):
        return ''

    def tickToData(self, jsn: dict) -> MarketData:
        raise NotImplementedError()

    def strToTradeType(self, s: str) -> TickType:
        raise NotImplementedError()

    def tradeReqToParams(self, req) -> dict:
        raise NotImplementedError()

    def currencyPairToString(self, cur: PairType) -> str:
        return cur.value[0].value + '/' + cur.value[1].value

    def orderTypeToString(self, typ: OrderType) -> str:
        raise NotImplementedError()
