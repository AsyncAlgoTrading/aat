from functools import lru_cache
from typing import List
from .data_source import RestAPIDataSource
from .enums import TradingType, ExchangeType, ExchangeType_to_string, TradeResult
from .structs import TradeRequest, TradeResponse
from .utils import (get_keys_from_environment, str_to_side,
                    exchange_type_to_ccxt_client, tradereq_to_ccxt_order,
                    parse_date)


class OrderEntry(RestAPIDataSource):
    @lru_cache(None)
    def oe_client(self):
        options = self.options()
        if options.trading_type == TradingType.SANDBOX:
            key, secret, passphrase = get_keys_from_environment(ExchangeType_to_string(self.exchange()) + '_SANDBOX')
        else:
            key, secret, passphrase = get_keys_from_environment(ExchangeType_to_string(self.exchange()))

        return exchange_type_to_ccxt_client(self.exchange())({
            'apiKey': key,
            'secret': secret,
            'password': passphrase,
            'enableRateLimit': True,
            'rateLimit': 250
        })

    def _extract_fields(self, order, exchange):
        side = order.get('side', order.get('info', {}).get('side'))
        filled = float(order.get('filled') or order.get('info', {}).get('filled_size') or order.get('info', {}).get('executed_amount'))
        price = order.get('price') or order.get('info', {}).get('price')
        datetime = order.get('datetime') or order.get('info', {}).get('timestamp')
        status = order.get('status')
        remaining = float(order.get('remaining') or order.get('info', {}).get('remaining') or order.get('info', {}).get('remaining_amount'))
        cost = order.get('fee', {}).get('cost', 0.0)

        # FIXME handle rejected orders
        if status is None and exchange == ExchangeType.GEMINI:
            # gemini
            original = float(order.get('info', {}).get('original_amount', 0.0))
            is_cancelled = order.get('info', {}).get('is_cancelled', False)
            if is_cancelled:
                status = TradeResult.REJECTED
            if filled == original or remaining <= 0:
                status = TradeResult.FILLED
            elif remaining < original and remaining > 0:
                status = TradeResult.PARTIAL
            elif remaining == original:
                status = TradeResult.PENDING
        elif status in ('OPEN',):
            status = TradeResult.PENDING
        return side, filled, price, datetime, status, cost, remaining

    def buy(self, req: TradeRequest) -> TradeResponse:
        '''execute a buy order'''
        params = tradereq_to_ccxt_order(req)
        order = self.oe_client().create_order(**params)
        side, filled, price, datetime, status, cost, remaining = self._extract_fields(order, req.exchange)
        resp = TradeResponse(request=req,
                             side=str_to_side(side),
                             exchange=req.exchange,
                             volume=float(filled),
                             price=float(price),
                             instrument=req.instrument,
                             time=parse_date(datetime),
                             status=status,
                             order_id=order['id'],
                             slippage=float(price) - req.price,
                             transaction_cost=cost,
                             remaining=float(remaining))
        return resp

    def sell(self, req: TradeRequest) -> TradeResponse:
        '''execute a sell order'''
        params = tradereq_to_ccxt_order(req)
        order = self.oe_client().create_order(**params)
        side, filled, price, datetime, status, cost, remaining = self._extract_fields(order, req.exchange)
        resp = TradeResponse(request=req,
                             side=str_to_side(side),
                             exchange=req.exchange,
                             volume=float(filled),
                             price=float(price),
                             instrument=req.instrument,
                             time=parse_date(datetime),
                             status=status,
                             order_id=order['id'],
                             slippage=float(price) - req.price,
                             transaction_cost=cost,
                             remaining=float(remaining))
        return resp

    def cancel(self, resp: TradeResponse):
        self.oe_client().cancel_order(resp.order_id)

    def cancelAll(self, order_ids: List[str] = None):
        if order_ids:
            for order_id in order_ids:
                self.oe_client().cancel_order(order_id)
        else:
            self.oe_client().cancel_all_orders()
