import json
from functools import lru_cache
from .utils.coinbase import CoinbaseMixins
from ..exchange import Exchange


class CoinbaseExchange(CoinbaseMixins, Exchange):
    @lru_cache(None)
    def subscription(self):
        return [json.dumps({"type": "subscribe", "product_id": self.currencyPairToString(x)}) for x in self.options().currency_pairs]

    @lru_cache(None)
    def heartbeat(self):
        return json.dumps({"type": "heartbeat", "on": True})
