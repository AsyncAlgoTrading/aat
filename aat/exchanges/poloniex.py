import json
from functools import lru_cache
from ..config import ExchangeConfig
from ..enums import ExchangeType
from ..exchange import Exchange
from .utils.poloniex import POLONIEX_PAIR_ID, PoloniexMixins


class PoloniexExchange(PoloniexMixins, Exchange):
    def __init__(self, exchange_type: ExchangeType, options: ExchangeConfig) -> None:
        super(PoloniexExchange, self).__init__(exchange_type, options)
        self._last = None
        self._orders = {}

    @lru_cache(None)
    def subscription(self):
        return [json.dumps({"command": "subscribe", "channel": "1002"})] + \
                [json.dumps({"command": "subscribe", "channel": POLONIEX_PAIR_ID.get(self.currencyPairToString(x))}) for x in self.options().currency_pairs],  # ticker data

    @lru_cache(None)
    def heartbeat(self):
        return json.dumps({"command": "subscribe", "channel": "1010"})
