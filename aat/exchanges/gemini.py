import aiohttp
import json
from aiostream import stream
from functools import lru_cache
from .utils.gemini import GeminiMixins
from ..define import EXCHANGE_MARKET_DATA_ENDPOINT
from ..enums import TickType
from ..exchange import Exchange
from ..logging import log


class GeminiExchange(GeminiMixins, Exchange):
    @lru_cache(None)
    def subscription(self):
        return [json.dumps({"type": "subscribe", "product_id": self.currencyPairToString(x)}) for x in self.options().currency_pairs]

    @lru_cache(None)
    def heartbeat(self):
        return ''

    async def run(self, engine) -> None:
        options = self.options()
        session = aiohttp.ClientSession()

        # startup and redundancy
        log.info('Starting....')
        self.ws = [await session.ws_connect(EXCHANGE_MARKET_DATA_ENDPOINT(self.exchange(), options.trading_type) % x) for x in self.subscription()]

        # set subscription for each ws
        for i, sub in enumerate(self.subscription()):
            self.ws[i]._subscription = sub
            log.info(f'Sending Subscription {sub}')

        log.info(f'Connected: {self.exchange()}')
        log.info('')
        log.critical(f'Starting algo trading: {self.exchange()}')
        try:
            while True:
                await self.receive()

        except KeyboardInterrupt:
            log.critical('Terminating program')
            engine.terminate()
            return

    async def receive(self) -> None:
        '''gemini has its own receive method because it uses 1 connection per symbol instead of multiplexing'''
        async def get_data_sub_pair(ws, sub=None):
            async for ret in ws:
                yield ret, sub

        async for val in stream.merge(*[get_data_sub_pair(self.ws[i], sub) for i, sub in enumerate(self.subscription())]):
            pair = json.loads(val[1]).get('product_id')
            jsn = json.loads(val[0].data)
            if jsn.get('type') == 'heartbeat':
                pass
            else:
                for item in jsn.get('events'):
                    item['symbol'] = pair
                    res = self.tickToData(item)

                    if not self._running:
                        pass

                    if res.type != TickType.HEARTBEAT:
                        self.callback(res.type, res)
