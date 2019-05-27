from ...enums import OrderType, PairType, TickType
from ...structs import MarketData


class KrakenMixins(object):
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
