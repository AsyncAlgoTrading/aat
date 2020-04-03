from datetime import datetime
from typing import List
from .config import RiskConfig
from .enums import Side, TradeResult, OrderType, RiskReason, ExchangeType
from .exchange import Exchange
from .logging import log
from .structs import TradeRequest, TradeResponse, Account, Instrument
from .utils import iterate_accounts


class Risk(object):
    def __init__(self, options: RiskConfig, exchanges: List[Exchange], accounts: List[Account]) -> None:
        self.trading_type = options.trading_type
        self.max_drawdown = options.max_drawdown
        self.max_risk = options.max_risk
        self.total_funds = options.total_funds

        self.outstanding = 0.0
        self.starting_funds = options.total_funds
        self.drawdown = 0.0

        self.exchanges = exchanges
        self.accounts = accounts

    def _constructResp(self,
                       side: Side,
                       exchange: ExchangeType,
                       instrument: Instrument,
                       order_type: OrderType,
                       vol: float,
                       price: float,
                       time: datetime,
                       status: bool,
                       strat: object,
                       reason: RiskReason) -> TradeRequest:
        resp = TradeRequest(side=side,
                            exchange=exchange,
                            instrument=instrument,
                            order_type=order_type,
                            volume=vol,
                            price=price,
                            time=time,
                            risk_check=status,
                            risk_reason=reason,
                            strategy=strat,
                            )
        return resp

    def request(self, req: TradeRequest) -> TradeRequest:
        # update risk as soon as order will go out
        log.info('Requesting %f @ %f', req.volume, req.price)
        total = req.volume * req.price
        total = total * -1 if req.side == Side.SELL else total
        max = self.max_risk / 100.0 * self.total_funds

        if (total + self.outstanding) <= max:
            # room for full volume
            log.info('Risk check passed for order: %s' % req)
            return self._constructResp(side=req.side,
                                       exchange=req.exchange,
                                       instrument=req.instrument,
                                       order_type=req.order_type,
                                       vol=req.volume,
                                       price=req.price,
                                       time=req.time,
                                       status=True,
                                       strat=req.strategy,
                                       reason=RiskReason.NONE)

        elif self.outstanding < max:
            # room for some volume
            volume = (max - self.outstanding) / req.price
            log.info('Risk check passed for partial order: %s' % req)
            return self._constructResp(side=req.side,
                                       exchange=req.exchange,
                                       instrument=req.instrument,
                                       order_type=req.order_type,
                                       vol=volume,
                                       price=req.price,
                                       time=req.time,
                                       status=True,
                                       strat=req.strategy,
                                       reason=RiskReason.PARTIAL)

        # no room for volume
        log.info('Risk check failed for order: %s' % req)
        return self._constructResp(side=req.side,
                                   exchange=req.exchange,
                                   instrument=req.instrument,
                                   order_type=req.order_type,
                                   vol=0.0,
                                   price=req.price,
                                   time=req.time,
                                   status=False,
                                   strat=req.strategy,
                                   reason=RiskReason.FULL)

    def requestBuy(self, req: TradeRequest):
        '''precheck for risk compliance'''
        return self.request(req)

    def requestSell(self, req: TradeRequest):
        '''precheck for risk compliance'''
        return self.request(req)

    def updateAccounts(self):
        '''update risk numbers'''
        log.critical('risk not fully implemented - updateRisk')
        value = 0.0

        for account in iterate_accounts(self.accounts):
            value += account.value

        if value < self.total_funds:
            log.info(f'restricting total funds from {self.total_funds} to {value}')
        elif value > self.total_funds:
            log.info(f'expanding total funds from {self.total_funds} to {value}')

        self.total_funds = value
        log.info(f'drawdown: {self.total_funds - self.starting_funds}')

    def update(self, resp: TradeResponse):
        '''update risk after execution'''
        log.critical('risk not fully implemented - update')
        self.updateAccounts()

        if resp.status == TradeResult.FILLED:
            # FIXME
            self.outstanding += abs(resp.volume * resp.price) * (1 if resp.side == Side.BUY else -1)

        elif resp.status == TradeResult.REJECTED:
            self.outstanding -= abs(resp.volume * resp.price) * (1 if resp.side == Side.BUY else -1)

    def cancel(self, resp: TradeResponse):
        '''update risk after cancelling or rejecting order'''
        log.critical('risk not fully implemented - cancel')
        self.updateAccounts()

        self.outstanding -= abs(resp.volume * resp.price) * (1 if resp.side == Side.BUY else -1)
