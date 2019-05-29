import ccxt
import pandas as pd
from datetime import datetime
from functools import lru_cache
from .data_source import RestAPIDataSource
from .enums import PairType, TradingType, ExchangeType
from .structs import TradeRequest, TradeResponse, Account
from .utils import (get_keys_from_environment, str_to_currency_type,
                    exchange_type_to_ccxt_client, tradereq_to_ccxt_order)
from .utils import elog as log


class OrderEntry(RestAPIDataSource):
    @lru_cache(None)
    def oe_client(self):
        options = self.options()
        if options.trading_type == TradingType.SANDBOX:
            key, secret, passphrase = get_keys_from_environment(self.exchange().value + '_SANDBOX')
        else:
            key, secret, passphrase = get_keys_from_environment(self.exchange().value)

        return exchange_type_to_ccxt_client(self.exchange())({
            'apiKey': key,
            'secret': secret,
            'password': passphrase,
            'enableRateLimit': True,
            })

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
            # FIXME
            value = balance
            # value = balance if currency == CurrencyType.USD else balance*self.lastPrice(str_currency_to_currency_pair_type(currency))['last']
            account = Account(id=id,
                              currency=currency,
                              balance=balance,
                              exchange=self.exchange(),
                              value=value,
                              asOf=datetime.now())
            accounts.append(account)
        # cache
        self._accounts = accounts
        return accounts

    def lastPrice(self, cur: PairType):
        try:
            return self.oe_client().fetchTicker(self.currencyPairToStringCCXT(cur))
        except (ccxt.ExchangeError, ValueError):
            return {'last': -1.0}

    @lru_cache(None)
    def currencyPairToStringCCXT(self, cur: PairType) -> str:
        return cur.value[0].value + '/' + cur.value[1].value

    def historical(self, timeframe='1m', since=None, limit=None):
        '''get historical data (for backtesting)'''
        client = self.oe_client()
        dfs = [{'pair': str(symbol), 'exchange': self.exchange().value, 'data': client.fetch_ohlcv(symbol=self.currencyPairToStringCCXT(symbol), timeframe=timeframe, since=since, limit=limit)}
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
        params = tradereq_to_ccxt_order(req)
        raise NotImplementedError()
        self.oe_client().create_order(**params)

    def cancelAll(self, resp: TradeResponse):
        return self.oe_client().cancel_all_orders()
