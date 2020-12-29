from aat.core import Position
from .risk import RiskManager


class StrategyManagerRiskMixin(object):
    _risk_mgr: RiskManager

    # *********************
    # Risk Methods        *
    # *********************
    def risk(self, position: Position = None) -> str:  # TODO
        return self._risk_mgr.risk(position=position)
