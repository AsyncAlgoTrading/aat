import base64
import hashlib
import hmac
import requests
import time
from requests.auth import AuthBase


# Create custom authentication for Exchange
class CoinbaseExchangeAuth(AuthBase):
    def __init__(self, api_url, ws_url, api_key, secret_key, passphrase):
        self.api_url = api_url
        self.ws_url = ws_url
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

    def products(self):
        return requests.get('{}/{}'.format(self.api_url, 'products'), auth=self).json()

    def accounts(self):
        return requests.get('{}/{}'.format(self.api_url, 'accounts'), auth=self).json()

    def account(self, account_id):
        return requests.get('{}/{}/{}'.format(self.api_url, 'accounts', account_id), auth=self).json()

    def newOrder(self, order_jsn):
        order_jsn['client_oid'] = self.order_id
        self.order_id += 1

        resp = requests.post('{}/{}'.format(self.api_url, 'orders'), data=order_jsn, auth=self)
        if resp.status_code == 200:
            return order_jsn['client_oid']
        return -1

    def cancelOrder(self, order_jsn):
        resp = requests.delete('{}/{}/{}?product_id={}'.format(self.api_url, 'orders', order_jsn['client_oid'], order_jsn['product_id']), auth=self)
        if resp.status_code == 200:
            return True
        return False

    def subscription(self, subscription):
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

    def orderBook(self, id):
        return requests.get('{}/{}/{}/book?level=3'.format(self.api_url, 'products', id), auth=self).json()
