import aiohttp
import base64
import hashlib
import hmac
import json
import requests
import time
from requests.auth import AuthBase
from datetime import datetime
from functools import lru_cache
from typing import List

# from aat import Instrument, InstrumentType, Account, Position
from aat import TradingType, ExchangeType, Instrument, InstrumentType, Position, Order, Trade, Side, OrderType, OrderFlag, Event, EventType


_REST = 'https://api.pro.coinbase.com'
_WS = 'wss://ws-feed.pro.coinbase.com'
_REST_SANDBOX = 'https://api-public.sandbox.pro.coinbase.com'
_WS_SANDBOX = 'wss://ws-feed-public.sandbox.pro.coinbase.com'

_SUBSCRIPTION = {
    "type": "subscribe",
    "product_ids": [
    ],
    "channels": [
        "full",
        "user",
        "heartbeat",
    ]
}


class CoinbaseExchangeClient(AuthBase):
    def __init__(self,
                 trading_type: TradingType,
                 exchange: ExchangeType,
                 api_key: str,
                 secret_key: str,
                 passphrase: str):
        self.trading_type = trading_type
        if self.trading_type == TradingType.SANDBOX:
            self.api_url = _REST_SANDBOX
            self.ws_url = _WS_SANDBOX
        else:
            self.api_url = _REST
            self.ws_url = _WS

        self.exchange = exchange

        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

        self.order_id = 0

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or b'').decode()
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message.encode(), hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest()).decode()

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request

    def _products(self):
        return requests.get('{}/{}'.format(self.api_url, 'products'), auth=self).json()

    def _accounts(self):
        return requests.get('{}/{}'.format(self.api_url, 'accounts'), auth=self).json()

    def _account(self, account_id):
        return requests.get('{}/{}/{}'.format(self.api_url, 'accounts', account_id), auth=self).json()

    def _newOrder(self, order_jsn):
        order_jsn['client_oid'] = self.order_id
        self.order_id += 1

        resp = requests.post('{}/{}'.format(self.api_url, 'orders'), data=order_jsn, auth=self)
        if resp.status_code == 200:
            return order_jsn['client_oid']
        return -1

    def _cancelOrder(self, order_jsn):
        resp = requests.delete('{}/{}/{}?product_id={}'.format(self.api_url, 'orders', order_jsn['client_oid'], order_jsn['product_id']), auth=self)
        if resp.status_code == 200:
            return True
        return False

    def _orderBook(self, id):
        return requests.get('{}/{}/{}/book?level=3'.format(self.api_url, 'products', id), auth=self).json()

    @lru_cache(None)
    def instruments(self):
        ret = []

        products = self._products()

        for product in products:
            first = product['base_currency']
            second = product['quote_currency']
            ret.append(
                Instrument(name='{}/{}'.format(first, second),
                           type=InstrumentType.PAIR,
                           exchange=self.exchange,
                           brokerId=product['id'],
                           leg1=self.currency(first),
                           leg2=self.currency(second),
                           leg1_side=Side.BUY,
                           leg2_side=Side.SELL)
            )
        return ret

    @lru_cache(None)
    def currency(self, symbol):
        return Instrument(name=symbol, type=InstrumentType.CURRENCY)

    @lru_cache(None)
    def accounts(self):
        ret = []
        accounts = self._accounts()
        if accounts == {'message': 'Unauthorized.'} or accounts == {'message': 'Invalid API Key'}:
            raise Exception('Coinbase auth failed')

        for account in accounts:
            acc_data = self._account(account['id'])
            if acc_data['trading_enabled'] and float(acc_data['balance']) > 0:
                # acc = Account(account['id'], exchange, [
                pos = Position(float(acc_data['balance']),
                               0.,
                               datetime.now(),
                               Instrument(acc_data['currency'],
                                          InstrumentType.CURRENCY,
                                          exchange=self.exchange),
                               self.exchange,
                               []
                               )
                ret.append(pos)
                # ]
                # )
                # ret.append(acc)
        return ret

    def newOrder(self, order: Order):
        jsn = {}

        if order.type == OrderType.LIMIT:
            jsn['type'] = 'limit'
            jsn['side'] = order.side.value.lower()
            jsn['price'] = order.price
            jsn['size'] = order.size

            if order.flag == OrderFlag.FILL_OR_KILL:
                jsn['time_in_force'] = 'FOK'
            elif order.flag == OrderFlag.IMMEDIATE_OR_CANCEL:
                jsn['time_in_force'] = 'IOC'
            else:
                jsn['time_in_force'] = 'GTC'

        elif order.type == OrderType.MARKET:
            jsn['type'] = 'market'
            jsn['side'] = order.side.value.lower()
            jsn['size'] = order.size

        else:
            jsn['type'] = order.stop_target.side.value.lower()
            jsn['price'] = order.stop_target.price
            jsn['size'] = order.stop_target.size

            if order.stop_target.side == Side.BUY:
                jsn['stop'] = 'entry'
            else:
                jsn['stop'] = 'loss'

            jsn['stop_price'] = order.price

            if order.stop_target.type == OrderType.LIMIT:
                jsn['type'] = 'limit'
                if order.flag == OrderFlag.FILL_OR_KILL:
                    jsn['time_in_force'] = 'FOK'
                elif order.flag == OrderFlag.IMMEDIATE_OR_CANCEL:
                    jsn['time_in_force'] = 'IOC'
                else:
                    jsn['time_in_force'] = 'GTC'

            elif order.stop_target.type == OrderType.MARKET:
                jsn['type'] = 'market'

        id = self._newOrder(jsn)
        if id > 0:
            order.id = id
            return True
        return False

    def cancelOrder(self, order: Order):
        jsn = {}
        jsn['client_oid'] = order.id
        jsn['product_id'] = order.instrument.brokerId
        return self._cancelOrder(jsn)

    def orderBook(self, subscriptions: List[Instrument]):
        # for sub in subscriptions:
        # ob = self._orderBook(instrument.brokerId)
        # print(ob)
        return []

    async def websocket(self, subscriptions: List[Instrument]):
        subscription = _SUBSCRIPTION.copy()
        for sub in subscriptions:
            subscription['product_ids'].append(sub.brokerId)
        timestamp = str(time.time())
        message = timestamp + 'GET' + '/users/self/verify'
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message.encode(), hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest()).decode()

        subscription.update({
            'signature': signature_b64,
            'timestamp': timestamp,
            'key': self.api_key,
            'passphrase': self.passphrase,
        })

        session = aiohttp.ClientSession()
        async with session.ws_connect(self.ws_url) as ws:
            await ws.send_str(json.dumps(subscription))

            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    x = json.loads(msg.data)
                    if x['type'] in ('subscriptions', 'heartbeat'):
                        # Skip
                        continue
                    elif x['type'] == 'received':
                        if x['order_type'] == 'market':
                            if 'size' in x and float(x['size']) <= 0:
                                continue
                            elif 'size' not in x and 'funds' in x:
                                print('TODO: funds')
                                continue
                            o = Order(float(x['size']), 0., Side(x['side'].upper()), Instrument(x['product_id'], InstrumentType.PAIR, self.exchange), self.exchange)
                        else:
                            o = Order(float(x['size']), float(x['price']), Side(x['side'].upper()), Instrument(x['product_id'], InstrumentType.PAIR, self.exchange), self.exchange)
                        e = Event(type=EventType.OPEN, target=o)
                        yield e
                    elif x['type'] == 'done':
                        if x['reason'] == 'canceled':
                            if 'price' not in x:
                                print('TODO: noprice')
                                continue
                            o = Order(float(x['remaining_size']), float(x['price']), Side(x['side'].upper()), Instrument(x['product_id'], InstrumentType.PAIR, self.exchange), self.exchange)
                            e = Event(type=EventType.CANCEL, target=o)
                            yield e
                        elif x['reason'] == 'filled':
                            continue
                        else:
                            print(x)
                    elif x['type'] == 'match':
                        o = Order(float(x['size']), float(x['price']), Side(x['side'].upper()), Instrument(x['product_id'], InstrumentType.PAIR, self.exchange), self.exchange)
                        o.filled = o.volume
                        t = Trade(float(x['size']), float(x['price']), [], o)
                        e = Event(type=EventType.TRADE, target=t)
                        yield e
                    elif x['type'] == 'open':
                        o = Order(float(x['remaining_size']), float(x['price']), Side(x['side'].upper()), Instrument(x['product_id'], InstrumentType.PAIR, self.exchange), self.exchange)
                        e = Event(type=EventType.OPEN, target=o)
                        yield e
                    else:
                        print(x)
