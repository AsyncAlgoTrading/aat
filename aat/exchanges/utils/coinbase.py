from datetime import datetime
from ...enums import OrderType, OrderSubType, PairType, TickType, TickType_from_string
from ...structs import MarketData, Instrument
from ...utils import parse_date, str_to_currency_pair_type, str_to_side, str_to_order_type


class CoinbaseMixins(object):
    def tickToData(self, jsn: dict) -> MarketData:
        if jsn.get('type') == 'received':
            return
        typ = self.strToTradeType(jsn.get('type'), jsn.get('reason', ''))
        time = parse_date(jsn.get('time')) if jsn.get('time') else datetime.now()
        price = float(jsn.get('price', 'nan'))
        volume = float(jsn.get('size', 'nan'))
        currency_pair = str_to_currency_pair_type(jsn.get('product_id')) if typ != TickType.ERROR else PairType.NONE

        instrument = Instrument(underlying=currency_pair)

        order_type = str_to_order_type(jsn.get('order_type', ''))
        side = str_to_side(jsn.get('side', ''))
        remaining_volume = float(jsn.get('remaining_size', 0.0))

        sequence = int(jsn.get('sequence', -1))
        ret = MarketData(time=time,
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

    def strToTradeType(self, s: str, reason: str = '') -> TickType:
        if s == 'match':
            return TickType.TRADE
        elif s in ('open', 'done', 'change', 'heartbeat'):
            if reason == 'canceled':
                return TickType.CANCEL
            elif reason == 'filled':
                return TickType.FILL
            return TickType_from_string(s.upper())
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
