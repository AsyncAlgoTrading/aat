import typing
if typing.TYPE_CHECKING:
    from aat.engine import StrategyManager


class StrategyRiskMixin(object):
    _manager: 'StrategyManager'

    ################
    # Risk Methods #
    ################
    def risk(self, position=None):
        '''Get risk metrics

        Args:
            position (Position): only get metrics on this position
        Returns:
            dict: metrics
        '''
        return self._manager.risk(position=position)
