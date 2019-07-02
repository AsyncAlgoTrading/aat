import operator
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import reduce
from typing import List, Dict
from .enums import TickType, TradeResult, Side, ExchangeType, PairType  # noqa: F401
from .exceptions import QueryException
from .execution import Execution
from .risk import Risk
from .strategy import TradingStrategy
from .structs import Instrument, MarketData, TradeRequest, TradeResponse


class QueryEngine(object):
    def __init__(self,
                 backtest: bool = False,
                 exchanges: List[ExchangeType] = None,
                 pairs: List[PairType] = None,
                 instruments: List[Instrument] = None,
                 risk: Risk = None,
                 execution: Execution = None,
                 total_funds: float = 0.0):
        self.executor = ThreadPoolExecutor(16)
        self._all = []

        self._portfolio_value = [] if backtest else [[datetime.now(), total_funds]]
        self._holdings = {}
        self._pending = {}

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

        self._strats = []
        self._risk = risk
        self._execution = execution

    def registerStrategy(self, strat: TradingStrategy):
        self._strats.append(strat)  # add to tickables

    def query_instruments(self, exchange=None) -> List[PairType]:
        if exchange:
            return self._instruments[exchange]
        else:
            return reduce(operator.concat, self._instruments.values())

    def query_exchanges(self) -> List[Dict]:
        return [{'exchange': name, 'instruments': self.query_instruments(name)}
                for name, ex in self._exchanges.items()]

    def _paginate(self, instrument: Instrument, lst: list, lst_sub: list, page: int = 1) -> list:
        if page is not None:
            from_ = -1*page*100
            to_ = -1*(page-1)*100
        else:
            # all results
            page = 0
            from_ = 0
            to_ = -1

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
            raise QueryException('Not found!')
        if exchange:
            if exchange not in self._last_price_by_asset_and_exchange[instrument]:
                raise QueryException('Not found!')
            return self._last_price_by_asset_and_exchange[instrument][exchange]
        if "ANY" not in self._last_price_by_asset_and_exchange[instrument]:
            raise QueryException('Not found!')
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

    def onTrade(self, data: MarketData) -> None:
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

        self._recalculate_value(data)

        if data.order_id in self._pending.keys():
            resp = self._pending[data.order_id]
            resp.volume = resp.remaining - data.remaining
            resp.remaining = data.remaining
            for strat in self._strats:
                strat.onFill(resp)
            self._risk.update(resp)

        if data.order_id in self._pending.keys() and data.remaining <= 0:
            del self._pending[data.order_id]

    def onCancel(self, data: MarketData) -> None:
        if data.order_id in self._pending.keys():
            resp = self._pending[data.order_id]
            del self._pending[data.order_id]
            self._risk.cancel(resp)

    def strategies(self):
        return self._strats

    def newPending(self, resp: TradeResponse) -> None:
        if resp.status == TradeResult.PENDING:
            self._pending[resp.order_id] = resp

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

    def _recalculate_value(self, data: MarketData) -> None:
        # TODO move to risk
        if data.instrument not in self._holdings:
            # nothing to do
            return
        volume = self._holdings[data.instrument][2]
        purchase_price = self._holdings[data.instrument][1]  # takes into account slippage/txn cost

        if self._portfolio_value == []:
            # start from first tick of data
            # TODO risk bounds?
            self._portfolio_value = [[data.time, volume*data.price, volume*(data.price-purchase_price)]]
        else:
            self._portfolio_value.append([data.time, volume*data.price, volume*(data.price-purchase_price)])

    def update_holdings(self, resp: TradeResponse) -> None:
        # TODO move to risk
        if resp.status in (TradeResult.REJECTED, TradeResult.PENDING, TradeResult.NONE):
            return
        if resp.instrument not in self._holdings:
            notional = resp.price * resp.volume*(1 if resp.side == Side.BUY else -1)
            self._holdings[resp.instrument] = \
                [notional, resp.price, resp.volume*(1 if resp.side == Side.BUY else -1)]
        else:
            notional = resp.price * resp.volume*(1 if resp.side == Side.BUY else -1)
            self._holdings[resp.instrument] = \
                [self._holdings[resp.instrument][0] + notional, resp.price, resp.volume*(1 if resp.side == Side.BUY else -1)]
