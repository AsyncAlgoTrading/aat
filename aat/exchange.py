import aiohttp
import json
from datetime import datetime
from functools import lru_cache
from typing import List
from .config import ExchangeConfig
from .enums import PairType, CurrencyType, ExchangeType, ExchangeType_to_string, TickType
from .market_data import MarketData
from .order_entry import OrderEntry
from .structs import Account, Instrument
from .exceptions import AATException
from .utils import findpath


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
    def accounts(self):
        client = self.oe_client()
        if not client:
            return {}
        balances = client.fetch_balance()

        accounts = {}

        for jsn in balances['info']:
            if isinstance(jsn, str):
                currency = jsn
                jsn = balances['info'][jsn]
            else:
                currency = jsn['currency']

            currency = CurrencyType(currency)
            if 'balance' in jsn:
                balance = float(jsn['balance'])
            elif 'amount' in jsn:
                balance = float(jsn['amount'])
            elif 'available' in jsn:
                balance = jsn['available']
            else:
                raise AATException('Cant read!')

            id = jsn.get('id', jsn['currency'])
            account = Account(id=id,
                              currency=currency,
                              balance=balance,
                              exchange=self.exchange(),
                              value=-1,
                              asOf=datetime.now())
            accounts[currency] = account
        return accounts

    @lru_cache(None)
    def options(self) -> ExchangeConfig:
        return self._options

    @lru_cache(None)
    def exchange(self) -> ExchangeType:
        return self._exchange

    @lru_cache(None)
    def currencies(self) -> List[CurrencyType]:
        return [CurrencyType(x) for x in self.oe_client().fetch_curencies()]

    @lru_cache(None)
    def markets(self) -> List[Instrument]:
        # TODO derivatives
        return [Instrument(underlying=PairType.from_string(m['symbol'])) for m in self.oe_client().fetch_markets()]

    def ticker(self,
               instrument: Instrument = None,
               currency: CurrencyType = None):
        if instrument:
            return self.oe_client().fetchTicker(str(instrument.underlying))
        elif currency:
            inst = Instrument(underlying=PairType.from_string(currency.value + '/USD'))

            if inst in self.markets():
                return self.oe_client().fetchTicker(str(inst.underlying))
            else:
                for stable in ('USD', 'USDC', 'USDT'):
                    try:
                        inst = Instrument(underlying=PairType.from_string(currency.value + '/' + stable))
                        inst1, inst2, i1_inverted, i2_inverted = findpath(inst, self.markets())
                        broken = False
                    except (AATException, ValueError):
                        broken = True
                if broken:
                    return {'last': 0.0}
                inst1_t = self.oe_client().fetchTicker(str(inst1.underlying))
                inst2_t = self.oe_client().fetchTicker(str(inst2.underlying))
                if i1_inverted:
                    inst1_t['last'] = 1.0 / inst1_t['last']
                if i2_inverted:
                    inst2_t['last'] = 1.0 / inst2_t['last']
                px = inst1_t['last'] * inst2_t['last']
                ret = inst1_t
                for key in ret:
                    if key == 'info':
                        ret[key] = {}
                    elif key == 'last':
                        ret[key] = px
                    else:
                        ret[key] = None
                return ret

    def historical(self, timeframe='1m', since=None, limit=None):
        '''get historical data (for backtesting)'''
        import pandas as pd
        client = self.oe_client()
        dfs = [{'pair': str(symbol), 'exchange': ExchangeType_to_string(self.exchange()), 'data': client.fetch_ohlcv(symbol=str(symbol), timeframe=timeframe, since=since, limit=limit)}
               for symbol in self.options().currency_pairs]
        df = pd.io.json.json_normalize(dfs, 'data', ['pair', 'exchange'])
        df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'pair', 'exchange']
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index(['timestamp', 'pair'], inplace=True)
        df.sort_index(inplace=True)
        return df

    def orderBook(self, level=1):
        '''get order book'''
        return self.oe_client().getProductOrderBook(level=level)

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
