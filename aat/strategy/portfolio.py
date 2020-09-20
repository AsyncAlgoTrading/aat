from ..core import Instrument, ExchangeType, StrategyManager
from ..core.portfolio import Portfolio


class StrategyPortfolioMixin(object):
    _manager: StrategyManager

    def positions(self, instrument: Instrument = None, exchange: ExchangeType = None):
        '''select all positions

        Args:
            instrument (Instrument): filter positions by instrument
            exchange (ExchangeType): filter positions by exchange
        Returns:
            list (Position): list of positions
        '''
        return self._manager.positions(instrument=instrument, exchange=exchange)

    def portfolio(self) -> Portfolio:
        '''Get portfolio object'''
        return self._manager.portfolio()

    def priceHistory(self, instrument: Instrument = None):
        '''Get price history for asset

        Args:
            instrument (Instrument): get price history for instrument
        Returns:
            DataFrame: price history
        '''
        return self._manager.priceHistory(instrument=instrument)
