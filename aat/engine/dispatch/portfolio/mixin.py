import pandas as pd
from typing import List, Union, TYPE_CHECKING

from aat.core import Instrument, ExchangeType, Position

from .manager import PortfolioManager
from .portfolio import Portfolio


if TYPE_CHECKING:
    from aat.strategy import Strategy


class StrategyManagerPortfolioMixin(object):
    _portfolio_mgr: PortfolioManager

    # *********************
    # Risk Methods        *
    # *********************
    def portfolio(self) -> Portfolio:
        return self._portfolio_mgr.portfolio()

    def positions(
        self,
        strategy: "Strategy",
        instrument: Instrument = None,
        exchange: ExchangeType = None,
    ) -> List[Position]:
        return self._portfolio_mgr.positions(
            strategy=strategy, instrument=instrument, exchange=exchange
        )

    def priceHistory(self, instrument: Instrument = None) -> Union[dict, pd.DataFrame]:
        return self._portfolio_mgr.priceHistory(instrument=instrument)
