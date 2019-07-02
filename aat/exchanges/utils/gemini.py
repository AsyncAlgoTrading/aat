from datetime import datetime
from ...enums import Side, OrderType, OrderSubType, PairType, TickType, TickType_from_string
from ...structs import MarketData, Instrument
from ...utils import str_to_currency_pair_type, str_to_side


class GeminiMixins(object):
    def tickToData(self, jsn: dict) -> MarketData:
        order_id = jsn.get('order_id', '')
        if order_id:
            import ipdb; ipdb.set_trace()
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

    def strToTradeType(self, s: str) -> TickType:
        s = s.upper()
        if s in ('BLOCK_TRADE', ):
            return TickType.TRADE
        elif s in ('AUCTION_INDICATIVE', 'AUCTION_OPEN'):
            return TickType.OPEN
        return TickType_from_string(s)

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
