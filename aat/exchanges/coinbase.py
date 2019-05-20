import json
from datetime import datetime
from functools import lru_cache
from ..enums import OrderType, OrderSubType, PairType, TickType, ChangeReason
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
        typ = self.strToTradeType(jsn.get('type'))
        reason = jsn.get('reason', '')
        time = parse_date(jsn.get('time')) if jsn.get('time') else datetime.now()
        price = float(jsn.get('price', 'nan'))
        volume = float(jsn.get('size', 'nan'))
        currency_pair = str_to_currency_pair_type(jsn.get('product_id')) if typ != TickType.ERROR else PairType.NONE

        instrument = Instrument(underlying=currency_pair)

        order_type = str_to_order_type(jsn.get('order_type', ''))
        side = str_to_side(jsn.get('side', ''))
        remaining_volume = float(jsn.get('remaining_size', 0.0))

        if reason == 'canceled':
            reason = ChangeReason.CANCELLED
        elif reason == '':
            reason = ChangeReason.NONE
        elif reason == 'filled':
            # FIXME
            reason = ChangeReason.NONE
            # reason = ChangeReason.FILLED
        else:
            reason = ChangeReason.NONE

        sequence = int(jsn.get('sequence', -1))
        ret = MarketData(time=time,
                         volume=volume,
                         price=price,
                         type=typ,
                         instrument=instrument,
                         remaining=remaining_volume,
                         reason=reason,
                         side=side,
                         exchange=self.exchange(),
                         order_type=order_type,
                         sequence=sequence)
        return ret

    def strToTradeType(self, s: str) -> TickType:
        if s == 'match':
            return TickType.TRADE
        elif s in ('received', 'open', 'done', 'change', 'heartbeat'):
            return TickType(s.upper())
        else:
            return TickType.ERROR

    def tradeReqToParams(self, req) -> dict:
        p = {}
        p['price'] = str(req.price)
        p['size'] = str(req.volume)
        p['product_id'] = self.currencyPairToString(req.instrument.currency_pair)
        p['type'] = self.orderTypeToString(req.order_type)

        if req.order_sub_type == OrderSubType.FILL_OR_KILL:
            p['time_in_force'] = 'FOK'
        elif req.order_sub_type == OrderSubType.POST_ONLY:
            p['post_only'] = '1'
        return p

    def currencyPairToString(self, cur: PairType) -> str:
        return cur.value[0].value + '-' + cur.value[1].value

    def orderTypeToString(self, typ: OrderType) -> str:
        return typ.value.lower()

    def reasonToTradeType(self, s: str) -> TickType:
        pass
