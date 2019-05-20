from .config import RiskConfig
from .structs import TradeRequest, TradeResponse, Instrument
from .enums import Side, TradeResult, OrderType, RiskReason
from .logging import RISK as rlog


class Risk(object):
    def __init__(self, options: RiskConfig) -> None:
        self.trading_type = options.trading_type
        self.max_drawdown = options.max_drawdown
        self.max_risk = options.max_risk
        self.total_funds = options.total_funds
        self.outstanding = 0.0  # type: float  # TODO get from open orders

        self.max_running_outstanding = 0.0
        self.max_running_outstanding_incr = []  # type: list

        self.max_running_drawdown = 0.0  # type: float
        self.max_running_drawdown_incr = []  # type: list

        self.max_running_risk = 0.0  # type: float
        self.max_running_risk_incr = []  # type: list

    def _constructResp(self,
                       side: Side,
                       instrument: Instrument,
                       order_type: OrderType,
                       vol: float,
                       price: float,
                       status: bool,
                       reason: RiskReason) -> TradeRequest:
        resp = TradeRequest(side=side, instrument=instrument, order_type=order_type, volume=vol, price=price, risk_check=status, risk_reason=reason)

        if status == TradeResult.FILLED:  # FIXME
            self.outstanding += abs(vol * price) * (1 if side == Side.BUY else -1)

            self.max_running_outstanding = max(self.max_running_outstanding,
                                               self.outstanding)
            self.max_running_outstanding_incr.append(
                self.max_running_outstanding)

            # TODO self.max_running_risk =
            # TODO self.max_running_drawdown =
        return resp

    def request(self, req: TradeRequest) -> TradeRequest:
        rlog.info('Requesting %f @ %f', req.volume, req.price)
        total = req.volume * req.price
        total = total * -1 if req.side == Side.SELL else total
        max = self.max_risk/100.0 * self.total_funds

        if (total + self.outstanding) <= max:
            # room for full volume
            rlog.info('Risk check passed for order: %s' % req)
            return self._constructResp(req.side, req.instrument, req.order_type, req.volume, req.price, True, RiskReason.NONE)

        elif self.outstanding < max:
            # room for some volume
            volume = (max - self.outstanding) / req.price
            rlog.info('Risk check passed for partial order: %s' % req)
            return self._constructResp(req.side, req.instrument, req.order_type, volume, req.price, True, RiskReason.PARTIAL)

        # no room for volume
        rlog.info('Risk check failed for order: %s' % req)
        return self._constructResp(req.side, req.instrument, req.order_type, req.volume, req.price, False, RiskReason.FULL)

    def requestBuy(self, req: TradeRequest):
        '''precheck for risk compliance'''
        return self.request(req)

    def requestSell(self, req: TradeRequest):
        '''precheck for risk compliance'''
        return self.request(req)

    def update(self, data: TradeResponse):
        '''update risk after execution'''
        pass
