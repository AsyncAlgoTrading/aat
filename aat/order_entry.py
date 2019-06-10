import pandas as pd
from datetime import datetime
from functools import lru_cache
from typing import List
from .data_source import RestAPIDataSource
from .enums import PairType, TradingType, CurrencyType, ExchangeType_to_string
from .exceptions import AATException
from .structs import TradeRequest, TradeResponse, Account, Instrument
from .utils import (get_keys_from_environment, str_to_currency_type,
                    exchange_type_to_ccxt_client, tradereq_to_ccxt_order,
                    findpath)
# from .utils import elog as log


class OrderEntry(RestAPIDataSource):
    @lru_cache(None)
    def oe_client(self):
        options = self.options()
        if options.trading_type == TradingType.SANDBOX:
            key, secret, passphrase = get_keys_from_environment(ExchangeType_to_string(self.exchange()) + '_SANDBOX')
        else:
            key, secret, passphrase = get_keys_from_environment(ExchangeType_to_string(self.exchange()))

        return exchange_type_to_ccxt_client(self.exchange())({
            'apiKey': key,
            'secret': secret,
            'password': passphrase,
            'enableRateLimit': True,
            })

    @lru_cache(None)
    def accounts(self):
        client = self.oe_client()
        if not client:
            return {}
        balances = client.fetch_balance()

        accounts = []

        for jsn in balances['info']:
            currency = str_to_currency_type(jsn['currency'])
            if 'balance' in jsn:
                balance = float(jsn['balance'])
            elif 'amount' in jsn:
                balance = float(jsn['amount'])

            id = jsn.get('id', jsn['currency'])
            account = Account(id=id,
                              currency=currency,
                              balance=balance,
                              exchange=self.exchange(),
                              value=-1,
                              asOf=datetime.now())
            accounts.append(account)
        return accounts

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
                try:
                    inst1, inst2, i1_inverted, i2_inverted = findpath(inst, self.markets())
                except AATException:
                    try:
                        inst = Instrument(underlying=PairType.from_string(currency.value + '/USDC'))
                        inst1, inst2, i1_inverted, i2_inverted = findpath(inst, self.markets())
                    except AATException:
                        return {'last': 0.0}
                inst1_t = self.oe_client().fetchTicker(str(inst1.underlying))
                inst2_t = self.oe_client().fetchTicker(str(inst2.underlying))
                if i1_inverted:
                    inst1_t['last'] = 1.0/inst1_t['last']
                if i2_inverted:
                    inst2_t['last'] = 1.0/inst2_t['last']
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
        client = self.oe_client()
        dfs = [{'pair': str(symbol), 'exchange': self.exchange().value, 'data': client.fetch_ohlcv(symbol=str(symbol), timeframe=timeframe, since=since, limit=limit)}
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

    def buy(self, req: TradeRequest) -> TradeResponse:
        '''execute a buy order'''
        params = tradereq_to_ccxt_order(req)
        raise NotImplementedError()
        self.oe_client().create_order(**params)

    def sell(self, req: TradeRequest) -> TradeResponse:
        '''execute a sell order'''
        params = tradereq_to_ccxt_order(req)
        raise NotImplementedError()
        self.oe_client().create_order(**params)

    def cancel(self, resp: TradeResponse):
        params = tradereq_to_ccxt_order(resp)
        raise NotImplementedError()
        self.oe_client().cancel_order(**params)

    def cancelAll(self, resp: TradeResponse):
        return self.oe_client().cancel_all_orders()
