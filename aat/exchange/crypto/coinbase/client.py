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

        # if running in sandbox mode, use sandbox urls
        if self.trading_type == TradingType.SANDBOX:
            self.api_url = _REST_SANDBOX
            self.ws_url = _WS_SANDBOX
        else:
            self.api_url = _REST
            self.ws_url = _WS

        # the coinbase ExchangeType
        self.exchange = exchange

        # coinbase api key
        self.api_key = api_key
        # coinbase api secret
        self.secret_key = secret_key
        # coinbase api passphrase
        self.passphrase = passphrase

        # user defined order id for mapping my orders to the messages the exchange sends me
        self.order_id = 0

        # sequence number for order book
        self.seqnum = {}

    def __call__(self, request):
        # This is used by `requests` to sign the requests
        # in the coinbase-specified auth scheme
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
        '''Fetch list of products from coinbase rest api'''
        return requests.get('{}/{}'.format(self.api_url, 'products'), auth=self).json()

    def _accounts(self):
        '''Fetch list of accounts from coinbase rest api'''
        return requests.get('{}/{}'.format(self.api_url, 'accounts'), auth=self).json()

    def _account(self, account_id):
        '''Fetch single account info from coinbase rest api'''
        return requests.get('{}/{}/{}'.format(self.api_url, 'accounts', account_id), auth=self).json()

    def _newOrder(self, order_jsn):
        '''create a new order'''

        # grab my own order id so i can match with received market data
        order_jsn['client_oid'] = self.order_id
        # monotonically increasing sequence
        self.order_id += 1

        # post my order to the rest endpoint
        resp = requests.post('{}/{}'.format(self.api_url, 'orders'), data=order_jsn, auth=self)

        # if successful, return new order id
        if resp.status_code == 200:
            return order_jsn['client_oid']

        # return -1 indicating unsuccessful
        return -1

    def _cancelOrder(self, order_jsn):
        '''delete an existing order'''
        # delete order with given order id
        resp = requests.delete('{}/{}/{}?product_id={}'.format(self.api_url, 'orders', order_jsn['client_oid'], order_jsn['product_id']), auth=self)

        # if successfully deleted, return True
        if resp.status_code == 200:
            return True
        # otherwise return false
        return False

    def _orderBook(self, id):
        # fetch an instrument's level 3 order book from the rest api
        return requests.get('{}/{}/{}/book?level=3'.format(self.api_url, 'products', id), auth=self).json()

    @lru_cache(None)
    def instruments(self):
        '''construct a list of instruments from the coinbase-returned json list of instruments'''
        ret = []

        # This will fetch a list of pairs
        products = self._products()

        for product in products:
            # separate pair into base and quote
            first = product['base_currency']
            second = product['quote_currency']

            # for each pair, construct both underlying currencies as well
            # as the pair object
            ret.append(
                Instrument(name='{}-{}'.format(first, second),
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
        # construct a base currency from the symbol
        return Instrument(name=symbol, type=InstrumentType.CURRENCY)

    @lru_cache(None)
    def accounts(self):
        '''fetch a list of coinbase accounts. These store quantities of InstrumentType.CURRENCY'''
        ret = []

        # fetch all accounts
        accounts = self._accounts()

        # if unauthorized or invalid api key, raise
        if accounts == {'message': 'Unauthorized.'} or accounts == {'message': 'Invalid API Key'}:
            raise Exception('Coinbase auth failed')

        # for each account
        for account in accounts:
            # grab the id to lookup info
            acc_data = self._account(account['id'])

            # if tradeable and positive balance
            if acc_data['trading_enabled'] and float(acc_data['balance']) > 0:
                # construct a position representing the balance

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
        '''given an aat Order, construct a coinbase order json'''
        jsn = {}

        if order.type == OrderType.LIMIT:
            jsn['type'] = 'limit'
            jsn['side'] = order.side.value.lower()
            jsn['price'] = order.price
            jsn['size'] = order.size

            # From the coinbase docs
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

        # submit the order json
        id = self._newOrder(jsn)
        if id > 0:
            # successful, set id on the order and return true
            order.id = id
            return True
        # otherwise return false indicating rejected
        return False

    def cancelOrder(self, order: Order):
        # given an aat Order, convert to json and cancel
        jsn = {}

        # coinbase expects client_oid and product_id, so map from
        # our internal api
        jsn['client_oid'] = order.id
        jsn['product_id'] = order.instrument.brokerId
        return self._cancelOrder(jsn)

    def orderBook(self, subscriptions: List[Instrument]):
        '''fetch level 3 order book for each Instrument in our subscriptions'''
        for sub in subscriptions:
            # fetch the order book
            # order book is of form:
            #       {'bids': [[price, volume, id]],
            #        'asks': [[price, volume, id]],
            #        'sequence': <some positive integer>}
            ob = self._orderBook(sub.brokerId)

            # set the last sequence number for when we
            # connect to websocket later
            self.seqnum[sub] = ob['sequence']

            # generate an open limit order for each bid
            for (bid, qty, id) in ob['bids']:
                o = Order(float(qty), float(bid), Side.BUY, sub, self.exchange, order_type=OrderType.LIMIT)
                yield Event(type=EventType.OPEN,
                            target=o)

            # generate an open limit order for each ask
            for (bid, qty, id) in ob['asks']:
                o = Order(float(qty), float(bid), Side.SELL, sub, self.exchange, order_type=OrderType.LIMIT)
                yield Event(type=EventType.OPEN,
                            target=o)

    async def websocket(self, subscriptions: List[Instrument]):
        # copy the base subscription template
        subscription = _SUBSCRIPTION.copy()

        # for each subcription, add symbol to product_ids
        for sub in subscriptions:
            subscription['product_ids'].append(sub.brokerId)

        # sign the message in a similar way to the rest api, but
        # using the message of GET/users/self/verify
        timestamp = str(time.time())
        message = timestamp + 'GET/users/self/verify'
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message.encode(), hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest()).decode()

        # update the subscription message with the signing info
        subscription.update({
            'signature': signature_b64,
            'timestamp': timestamp,
            'key': self.api_key,
            'passphrase': self.passphrase,
        })

        # construct a new websocket session
        session = aiohttp.ClientSession()

        # connect to the websocket
        async with session.ws_connect(self.ws_url) as ws:
            # send the subscription
            await ws.send_str(json.dumps(subscription))

            # for each message returned
            async for msg in ws:
                # only handle text messages
                if msg.type == aiohttp.WSMsgType.TEXT:
                    # load the data as json
                    x = json.loads(msg.data)

                    # skip earlier messages that our order book
                    # already reflects
                    if 'sequence' in x:
                        inst = Instrument(x['product_id'], InstrumentType.PAIR, self.exchange)
                        if x.get('sequence', float('inf')) < self.seqnum.get(inst, 0):
                            # if msg has a sequence number, and that number is < the last sequence number
                            # of the order book snapshot, ignore
                            continue

                    # ignore subscription  and heartbeat messages
                    if x['type'] in ('subscriptions', 'heartbeat'):
                        # TODO yield heartbeats?
                        continue

                    elif x['type'] == 'received':
                        # generate new Open events for
                        # received orders
                        if x['order_type'] == 'market':
                            if 'size' in x and float(x['size']) <= 0:
                                # ignore zero size orders
                                # TODO why do we even get these?
                                continue
                            elif 'size' not in x and 'funds' in x:
                                print('TODO: funds')
                                # TODO can't handle these yet, no mapping from funds to size/price
                                continue

                            # create a market data order from the event data
                            # TODO set something for price? float('inf') ?
                            o = Order(float(x['size']), 0., Side(x['side'].upper()), Instrument(x['product_id'], InstrumentType.PAIR, self.exchange), self.exchange)
                        else:
                            # create limit order from the event data
                            o = Order(float(x['size']), float(x['price']), Side(x['side'].upper()), Instrument(x['product_id'], InstrumentType.PAIR, self.exchange), self.exchange)

                        # yield an open event for the new order
                        e = Event(type=EventType.OPEN, target=o)
                        yield e

                    elif x['type'] == 'done':
                        # done events can be canceled or filled
                        if x['reason'] == 'canceled':
                            # if cancelled
                            if 'price' not in x:
                                # cancel this event if we have a full local order book
                                # where we can determine the original order
                                print('TODO: noprice')
                                continue

                            # FIXME don't use remaining_size, lookup original size in order book
                            o = Order(float(x['remaining_size']), float(x['price']), Side(x['side'].upper()), Instrument(x['product_id'], InstrumentType.PAIR, self.exchange), self.exchange)
                            e = Event(type=EventType.CANCEL, target=o)
                            yield e

                        elif x['reason'] == 'filled':
                            # Will have a match event
                            # TODO route these to full local order book
                            continue

                        else:
                            # TODO unhandled
                            # this should never print
                            print(x)

                    elif x['type'] == 'match':
                        # Generate a trade event
                        # First, create an order from the event
                        o = Order(float(x['size']), float(x['price']), Side(x['side'].upper()), Instrument(x['product_id'], InstrumentType.PAIR, self.exchange), self.exchange)

                        # set filled to volume so we see it as "done"
                        o.filled = o.volume

                        # create a trader with this order as the taker
                        # makers would be accumulated via the
                        # `elif x['reason'] == 'filled'` block above
                        t = Trade(float(x['size']), float(x['price']), [], o)
                        e = Event(type=EventType.TRADE, target=t)
                        yield e

                    elif x['type'] == 'open':
                        # Vanilla open events
                        # TODO how are these differentiated from received?
                        o = Order(float(x['remaining_size']), float(x['price']), Side(x['side'].upper()), Instrument(x['product_id'], InstrumentType.PAIR, self.exchange), self.exchange)
                        e = Event(type=EventType.OPEN, target=o)
                        yield e
                    else:
                        # TODO unhandled
                        # this should never print
                        print(x)
