from typing import List
from .enums import TickType, Side, ExchangeType, CurrencyType, PairType  # noqa: F401
from .structs import Instrument, MarketData


class QueryEngine(object):
    def __init__(self,
                 exchanges: List[ExchangeType] = None,
                 pairs: List[PairType] = None,
                 instruments: List[Instrument] = None):
        self._all = []

        self._trades = []
        self._trades_by_instrument = {}

        self._pairs = pairs
        self._instruments = instruments

        self._orders_by_currency = {}
        self._orders_by_exchange = {}
        self._orders_by_exchange_and_currency = {}

    def query_instruments(self) -> List[PairType]:
        return self._instruments

    def query_trades(self,
                     instrument: Instrument = None,
                     page: int = 1) -> List[MarketData]:
        from_ = -1*page*100
        to_ = -1*(page-1)*100

        if instrument:
            return self._trades_by_instrument[instrument][from_:to_] \
                if page > 1 else \
                self._trades_by_instrument[instrument][from_:]
        return self._trades[from_:to_] \
            if page > 1 else \
            self._trades[from_:]

    def push(self, data: MarketData) -> None:
        self._all.append(data)

        if data.type == TickType.TRADE:
            self._trades.append(data)
            if data.instrument not in self._trades_by_instrument:
                self._trades_by_instrument[data.instrument] = []
            self._trades_by_instrument[data.instrument].append(data)
