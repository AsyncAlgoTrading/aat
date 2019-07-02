import json
from functools import lru_cache
from datetime import datetime
from ..enums import OrderSubType, PairType, TickType, TickType_from_string
from ..exchange import Exchange
from ..structs import MarketData, Instrument
from ..utils import parse_date, str_to_currency_pair_type, str_to_side, str_to_order_type


class CoinbaseExchange(Exchange):
    @lru_cache(None)
    def subscription(self):
        return [json.dumps({"type": "subscribe", "product_id": self.currencyPairToString(x)}) for x in self.options().currency_pairs]

    @lru_cache(None)
    def heartbeat(self):
        return json.dumps({"type": "heartbeat", "on": True})

    def tickToData(self, jsn: dict) -> MarketData:
        if jsn.get('type') == 'received':
            return

        s = jsn.get('type')
        reason = jsn.get('reason')
        if s == 'match' or (s == 'done' and reason == 'filled'):
            typ = TickType.TRADE
        elif s in ('open', 'done', 'change', 'heartbeat'):
            if reason == 'canceled':
                typ = TickType.CANCEL
            typ = TickType_from_string(s.upper())
        else:
            typ = TickType.ERROR

        order_id = jsn.get('order_id', jsn.get('maker_order_id', ''))
        time = parse_date(jsn.get('time')) if jsn.get('time') else datetime.now()
        price = float(jsn.get('price', 'nan'))
        volume = float(jsn.get('size', 'nan'))
        currency_pair = str_to_currency_pair_type(jsn.get('product_id')) if typ != TickType.ERROR else PairType.NONE

        instrument = Instrument(underlying=currency_pair)

        order_type = str_to_order_type(jsn.get('order_type', ''))
        side = str_to_side(jsn.get('side', ''))
        remaining_volume = float(jsn.get('remaining_size', 0.0))

        sequence = int(jsn.get('sequence', -1))
        ret = MarketData(order_id=order_id,
                         time=time,
                         volume=volume,
                         price=price,
                         type=typ,
                         instrument=instrument,
                         remaining=remaining_volume,
                         side=side,
                         exchange=self.exchange(),
                         order_type=order_type,
                         sequence=sequence)
        return ret

    def tradeReqToParams(self, req) -> dict:
        p = {}
        p['price'] = str(req.price)
        p['size'] = str(req.volume)
        p['product_id'] = req.instrument.currency_pair.value[0].value + '-' + req.instrument.currency_pair.value[1].value
        p['type'] = req.order_type.value.lower()

        if req.order_sub_type == OrderSubType.FILL_OR_KILL:
            p['time_in_force'] = 'FOK'
        elif req.order_sub_type == OrderSubType.POST_ONLY:
            p['post_only'] = '1'
        return p
