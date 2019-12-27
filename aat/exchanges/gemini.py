import aiohttp
import base64
import json
import hashlib
import hmac
import time
from aiostream import stream
from datetime import datetime
from functools import lru_cache
from ..define import EXCHANGE_MARKET_DATA_ENDPOINT
from ..enums import TickType, TickType_from_string, PairType
from ..exchange import Exchange
from ..logging import log
from ..structs import MarketData, Instrument
from ..utils import str_to_side


class GeminiExchange(Exchange):
    @lru_cache(None)
    def subscription(self):
        return [json.dumps({"type": "subscribe", "product_id": x.value[0].value + x.value[1].value}) for x in self.options().currency_pairs]

    @lru_cache(None)
    def heartbeat(self):
        return ''

    async def run(self, engine) -> None:
        options = self.options()
        # private events
        gemini_api_key = self.oe_client().apiKey
        gemini_api_secret = self.oe_client().secret.encode()

        payload = {"request": "/v1/order/events", "nonce": int(time.time() * 1000)}
        encoded_payload = json.dumps(payload).encode()
        b64 = base64.b64encode(encoded_payload)
        signature = hmac.new(gemini_api_secret, b64, hashlib.sha384).hexdigest()

        session = aiohttp.ClientSession(headers={
            'X-GEMINI-PAYLOAD': b64.decode(),
            'X-GEMINI-APIKEY': gemini_api_key,
            'X-GEMINI-SIGNATURE': signature
        })

        # startup and redundancy
        log.info('Starting....')
        self.ws = [await session.ws_connect(EXCHANGE_MARKET_DATA_ENDPOINT(self.exchange(), options.trading_type) % x) for x in self.subscription()]
        private_events = await session.ws_connect("wss://api.gemini.com/v1/order/events")
        self.ws.append(private_events)

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

        # add one for private stream
        async for val in stream.merge(*[get_data_sub_pair(self.ws[i], sub) for i, sub in enumerate(self.subscription() + [None])]):
            jsn = json.loads(val[0].data)

            if isinstance(jsn, dict) and 'events' in jsn:
                events = jsn.get('events', [])
            elif not isinstance(jsn, list):
                events = [jsn]
            else:
                events = jsn

            if val[1]:
                # data stream
                pair = json.loads(val[1]).get('product_id')
            else:
                # private events
                pair = None

            for item in events:
                if item.get('type', 'subscription_ack') in ('subscription_ack', 'heartbeat'):
                    # can skip these
                    continue
                if item.get('type') == 'accepted':
                    # can ignore these as well, will have a fill and/or booked
                    # https://docs.gemini.com/websocket-api/#workflow
                    continue
                if item.get('type') == 'closed':
                    # can ignore these as well, will have a fill or cancelled
                    # https://docs.gemini.com/websocket-api/#workflow
                    continue

                if pair is None:
                    # private events
                    pair = item['symbol']

                item['symbol'] = pair
                res = self.tickToData(item)

                if not self._running:
                    pass

                if res.type != TickType.HEARTBEAT:
                    self.callback(res.type, res)

    def tickToData(self, jsn: dict) -> MarketData:
        order_id = jsn.get('order_id', '') or str(jsn.get('tid', ''))
        time = datetime.now()
        price = float(jsn.get('price', 'nan'))
        volume = float(jsn.get('amount', 0.0))

        s = jsn.get('type').upper()
        if s in ('BLOCK_TRADE', 'FILL'):  # Market data can't trigger fill event
            typ = TickType.TRADE
        elif s in ('AUCTION_INDICATIVE', 'AUCTION_OPEN', 'BOOKED', 'INITIAL'):
            typ = TickType.OPEN
        elif s in ('CANCELLED',):
            typ = TickType.CANCEL
        else:
            typ = TickType_from_string(s)
        delta = float(jsn.get('delta', 0.0))

        if typ == TickType.CHANGE and not volume:
            delta = float(jsn.get('delta', 'nan'))
            volume = delta
            # typ = self.reasonToTradeType(reason)

        side = str_to_side(jsn.get('side', ''))
        remaining_volume = float(jsn.get('remaining', jsn.get('remaining_amount', 'nan')))
        sequence = -1

        if 'symbol' not in jsn:
            return

        currency_pair = PairType.from_string(jsn.get('symbol'))
        instrument = Instrument(underlying=currency_pair)

        ret = MarketData(order_id=order_id,
                         time=time,
                         volume=volume,
                         price=price,
                         type=typ,
                         instrument=instrument,
                         remaining=remaining_volume,
                         side=side,
                         exchange=self.exchange(),
                         sequence=sequence)
        return ret
