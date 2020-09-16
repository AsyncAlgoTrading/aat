
class StrategyManagerRiskMixin(object):
    # *********************
    # Risk Methods        *
    # *********************
    def positions(self, instrument=None, exchange=None, side=None):
        return self._portfolio_mgr.positions(instrument=instrument, exchange=exchange, side=side)

    def risk(self, position=None):
        return self._risk_mgr.risk(position=position)

    def priceHistory(self, instrument=None):
        return self._risk_mgr.priceHistory(instrument=instrument)
