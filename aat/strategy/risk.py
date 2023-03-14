from typing import Optional, TYPE_CHECKING

from aat.core import Position

if TYPE_CHECKING:
    from aat.engine import StrategyManager


class StrategyRiskMixin(object):
    _manager: "StrategyManager"

    ################
    # Risk Methods #
    ################
    def risk(self, position: Optional[Position] = None) -> str:  # TODO
        """Get risk metrics

        Args:
            position (Position): only get metrics on this position
        Returns:
            dict: metrics
        """
        return self._manager.risk(position=position)
