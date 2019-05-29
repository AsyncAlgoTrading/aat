from typing import List
from concurrent.futures import ThreadPoolExecutor
from .enums import TickType, Side, ExchangeType, CurrencyType, PairType  # noqa: F401
from .structs import Instrument, MarketData, TradeRequest, TradeResponse


class QueryEngine(object):
    def __init__(self,
                 exchanges: List[ExchangeType] = None,
                 pairs: List[PairType] = None,
                 instruments: List[Instrument] = None):
        self.executor = ThreadPoolExecutor(16)
        self._all = []

        self._trades = []
        self._trades_by_instrument = {}

        self._pairs = pairs
        self._instruments = instruments
        self._exchanges = exchanges

        self._last_price_by_asset_and_exchange = {}

        self._trade_reqs = []
        self._trade_resps = []
        self._trade_reqs_by_instrument = {}
        self._trade_resps_by_instrument = {}

    def query_instruments(self) -> List[PairType]:
        return self._instruments

    def query_exchanges(self) -> List[ExchangeType]:
        return self._exchanges

    def _paginate(self, instrument: Instrument, lst: list, lst_sub: list, page: int = 1)-> list:
        from_ = -1*page*100
        to_ = -1*(page-1)*100

        if instrument:
            return lst_sub[instrument][from_:to_] \
                if page > 1 else lst_sub[instrument][from_:]
        return lst[from_:to_] \
            if page > 1 else lst[from_:]

    def query_lastpriceall(self) -> List[MarketData]:
        return [m for exs in self._last_price_by_asset_and_exchange.values()
                for m in exs.values()]

    def query_lastprice(self,
                        instrument: Instrument,
                        exchange: ExchangeType = None) -> MarketData:
        if instrument not in self._last_price_by_asset_and_exchange:
            raise Exception('Not found!')
        if exchange:
            if exchange not in self._last_price_by_asset_and_exchange[instrument]:
                raise Exception('Not found!')
            return self._last_price_by_asset_and_exchange[instrument][exchange]
        if "ANY" not in self._last_price_by_asset_and_exchange[instrument]:
            raise Exception('Not found!')
        return self._last_price_by_asset_and_exchange[instrument]["ANY"]

    def query_trades(self,
                     instrument: Instrument = None,
                     page: int = 1) -> List[MarketData]:
        return self._paginate(instrument,
                              self._trades,
                              self._trades_by_instrument,
                              page)

    def query_tradereqs(self,
                        instrument: Instrument = None,
                        page: int = 1) -> List[TradeRequest]:
        return self._paginate(instrument,
                              self._trade_reqs,
                              self._trade_reqs_by_instrument,
                              page)

    def query_traderesps(self,
                         instrument: Instrument = None,
                         page: int = 1) -> List[TradeResponse]:
        return self._paginate(instrument,
                              self._trade_resps,
                              self._trade_resps_by_instrument,
                              page)

    def push(self, data: MarketData) -> None:
        self._all.append(data)

        if data.type == TickType.TRADE:
            self._trades.append(data)
            if data.instrument not in self._trades_by_instrument:
                self._trades_by_instrument[data.instrument] = []
            self._trades_by_instrument[data.instrument].append(data)
            if data.instrument not in self._last_price_by_asset_and_exchange:
                self._last_price_by_asset_and_exchange[data.instrument] = {}
            self._last_price_by_asset_and_exchange[data.instrument][data.exchange] = data
            self._last_price_by_asset_and_exchange[data.instrument]['ANY'] = data
            print("here", self._last_price_by_asset_and_exchange[data.instrument][data.exchange])

    def push_tradereq(self, req: TradeRequest) -> None:
        self._trade_reqs.append(req)
        if req.instrument not in self._trade_reqs_by_instrument:
            self._trade_reqs_by_instrument[req.instrument] = []
        self._trade_reqs_by_instrument[req.instrument].append(req)

    def push_traderesp(self, resp: TradeResponse) -> None:
        self._trade_resps.append(resp)
        if resp.instrument not in self._trade_resps_by_instrument:
            self._trade_resps_by_instrument[resp.instrument] = []
        self._trade_resps_by_instrument[resp.instrument].append(resp)
