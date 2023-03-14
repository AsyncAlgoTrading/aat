from aat.core import Position
from .risk import RiskManager
from typing import Optional


class StrategyManagerRiskMixin(object):
    _risk_mgr: RiskManager

    # *********************
    # Risk Methods        *
    # *********************
    def risk(self, position: Optional[Position] = None) -> str:  # TODO
        return self._risk_mgr.risk(position=position)
