import aiohttp
import json
from aiostream import stream
from datetime import datetime
from functools import lru_cache
from ..define import EXCHANGE_MARKET_DATA_ENDPOINT
from ..enums import Side, OrderType, OrderSubType, PairType, TickType
from ..exchange import Exchange
from ..logging import LOG as log
from ..structs import MarketData, Instrument, TradeResponse
from ..utils import str_to_currency_pair_type, str_to_side


class GeminiExchange(Exchange):
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
                        if self._query_engine:
                            self._query_engine.push(res)


                    if res.type == TickType.TRADE:
                        self._last = res
                        self.callback(TickType.TRADE, res)
                    elif res.type == TickType.RECEIVED:
                        self.callback(TickType.RECEIVED, res)
                    elif res.type == TickType.OPEN:
                        self.callback(TickType.OPEN, res)
                    elif res.type == TickType.FILL:
                        self.callback(TickType.FILL, res)
                    elif res.type == TickType.CANCEL:
                        self.callback(TickType.CANCEL, res)
                    elif res.type == TickType.CHANGE:
                        self.callback(TickType.CHANGE, res)
                    elif res.type == TickType.HEARTBEAT:
                        # TODO anything?
                        pass
                    else:
                        self.callback(TickType.ERROR, res)

    def cancel(self, resp: TradeResponse):
        '''cancel an order'''
        raise NotImplementedError()

    def cancelAll(self) -> None:
        '''cancel all orders'''
        log.critical('Cancelling all active orders')
        self._client.cancel_all_active_orders()

    def tickToData(self, jsn: dict) -> MarketData:
        time = datetime.now()
        price = float(jsn.get('price', 'nan'))
        volume = float(jsn.get('amount', 0.0))
        typ = self.strToTradeType(jsn.get('type'))
        delta = float(jsn.get('delta', 0.0))

        if typ == TickType.CHANGE and not volume:
            delta = float(jsn.get('delta', 'nan'))
            volume = delta
            # typ = self.reasonToTradeType(reason)

        side = str_to_side(jsn.get('side', ''))
        remaining_volume = float(jsn.get('remaining', 'nan'))
        sequence = -1

        if 'symbol' not in jsn:
            return

        currency_pair = str_to_currency_pair_type(jsn.get('symbol'))
        instrument = Instrument(underlying=currency_pair)

        ret = MarketData(time=time,
                         volume=volume,
                         price=price,
                         type=typ,
                         instrument=instrument,
                         remaining=remaining_volume,

                         side=side,
                         exchange=self.exchange(),
                         sequence=sequence)
        return ret

    def strToTradeType(self, s: str) -> TickType:
        return TickType(s.upper())

    def reasonToTradeType(self, s: str) -> TickType:
        s = s.upper()
        if 'CANCEL' in s:
            return TickType.CANCEL
        if 'PLACE' in s:
            return TickType.OPEN
        if 'INITIAL' in s:
            return TickType.OPEN

    def tradeReqToParams(self, req) -> dict:
        p = {}
        p['price'] = str(req.price)
        p['size'] = str(req.volume)
        p['product_id'] = self.currencyPairToString(req.instrument.currency_pair)
        p['type'] = self.orderTypeToString(req.order_type)

        if p['type'] == OrderType.MARKET:
            if req.side == Side.BUY:
                p['price'] = 100000000.0
            else:
                p['price'] = .00000001

        if req.order_sub_type == OrderSubType.FILL_OR_KILL:
            p['time_in_force'] = 'FOK'
        elif req.order_sub_type == OrderSubType.POST_ONLY:
            p['post_only'] = '1'
        return p

    def currencyPairToString(self, cur: PairType) -> str:
        return cur.value[0].value + cur.value[1].value

    def orderTypeToString(self, typ: OrderType) -> str:
        return typ.value.lower()
