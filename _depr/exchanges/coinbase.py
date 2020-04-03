import json
from functools import lru_cache
from datetime import datetime
from ..enums import PairType, TickType, TickType_from_string
from ..exchange import Exchange
from ..structs import MarketData, Instrument
from ..utils import parse_date, str_to_side, str_to_order_type


class CoinbaseExchange(Exchange):
    @lru_cache(None)
    def subscription(self):
        return [json.dumps({"type": "subscribe", "product_id": x.value[0].value + '-' + x.value[1].value}) for x in self.options().currency_pairs]

    @lru_cache(None)
    def heartbeat(self):
        return json.dumps({"type": "heartbeat", "on": True})

    def tickToData(self, jsn: dict) -> MarketData:
        '''convert a jsn tick off the websocket to a MarketData struct'''
        if jsn.get('type') == 'received':
            return

        s = jsn.get('type').upper()
        reason = jsn.get('reason', '').upper()
        if s == 'MATCH' or (s == 'DONE' and reason == 'FILLED'):
            typ = TickType.TRADE
        elif s in ('OPEN', 'DONE', 'CHANGE', 'HEARTBEAT'):
            if reason == 'CANCELED':
                typ = TickType.CANCEL
            elif s == 'DONE':
                typ = TickType.FILL
            else:
                typ = TickType_from_string(s.upper())
        else:
            typ = TickType.ERROR

        order_id = jsn.get('order_id', jsn.get('maker_order_id', ''))
        time = parse_date(jsn.get('time')) if jsn.get('time') else datetime.now()

        if typ in (TickType.CANCEL, TickType.OPEN):
            volume = float(jsn.get('remaining_size', 'nan'))
        else:
            volume = float(jsn.get('size', 'nan'))
        price = float(jsn.get('price', 'nan'))

        currency_pair = PairType.from_string(jsn.get('product_id')) if typ != TickType.ERROR else PairType.NONE

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
