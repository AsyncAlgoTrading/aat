import operator
# from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import reduce
from typing import List, Dict
from .enums import TickType, TradeResult, Side, ExchangeType, PairType, CurrencyType  # noqa: F401
from .exceptions import QueryException
from .execution import Execution
from .risk import Risk
from .strategy import TradingStrategy
from .structs import Instrument, MarketData, TradeRequest, TradeResponse


class QueryEngine(object):
    def __init__(self,
                 exchanges: List[ExchangeType] = None,
                 pairs: List[PairType] = None,
                 instruments: List[Instrument] = None,
                 accounts=None,
                 risk: Risk = None,
                 execution: Execution = None):
        # self._executor = ThreadPoolExecutor(16)
        self._all = []

        self._accounts = accounts

        self._portfolio_value_by_instrument = {}
        self._portfolio_value = [[datetime.now(), risk.total_funds, 0.0]]
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
        self._strats.append(strat)

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
        # TODO move to Risk
        if data.instrument not in self._holdings:
            # nothing to do
            return

        volume = self._holdings[data.instrument]._volume
        instrument = str(data.instrument)
        value = self._holdings[data.instrument]._avg_price * volume
        pnl = self._holdings[data.instrument]._pnl

        if volume < 0:
            # sanity check, no shorting for now!
            raise Exception('Something has gone wrong!')

        if instrument not in self._portfolio_value_by_instrument:
            self._portfolio_value_by_instrument[instrument] = []
        self._portfolio_value_by_instrument[instrument].append([data.time, instrument, value + pnl, pnl])

        pnl = sum(x._pnl for x in self._holdings.values())
        self._portfolio_value.append([data.time, self._portfolio_value[-1][1], pnl])

    def update_holdings(self, resp: TradeResponse) -> None:
        if resp.status in (TradeResult.REJECTED, TradeResult.PENDING, TradeResult.NONE):
            return
        if resp.instrument not in self._holdings:
            self._holdings[resp.instrument] = pnl_helper()
        self._holdings[resp.instrument].exec(resp.volume, resp.price)


def sign(x): return (1, -1)[x < 0]


class pnl_helper(object):
    def __init__(self):
        self._records = []
        self._pnl = 0.0
        self._px = None
        self._volume = None
        self._realized = 0.0
        self._avg_price = self._px

    def exec(self, amt, px):
        if self._px is None:
            self._px = px
            self._volume = amt
            self._avg_price = self._px
            self._records.append({'volume': self._volume, 'px': px, 'apx': self._avg_price, 'pnl': self._pnl+self._realized, 'unrealized': self._pnl, 'realized': self._realized})
            return
        if sign(amt) == sign(self._volume):
            # increasing position
            self._avg_price = (self._avg_price*self._volume + px*amt)/(self._volume + amt)
            self._volume += amt
            self._pnl = (self._volume * (px-self._avg_price))
        else:
            if abs(amt) > abs(self._shares):
                # do both
                diff = self._volume
                self._volume = amt + self._volume

                # take profit/loss
                self._realized += (diff * (px - self._avg_price))

                # increasing position
                self._avg_price = px

            else:
                # take profit/loss
                self._volume += amt

                self._pnl = (self._volume * (px-self._avg_price))
                self._realized += (amt * (self._avg_price-px))
        self._records.append({'volume': self._volume, 'px': px, 'apx': self._avg_price, 'pnl': self._pnl+self._realized, 'unrealized': self._pnl, 'realized': self._realized})
