import pandas as pd  # type: ignore
from typing import Optional, List

from aat.core import Event, Trade, Instrument, ExchangeType, Position
from aat.core.handler import EventHandler

from ..base import ManagerBase
from .portfolio import Portfolio


class PortfolioManager(ManagerBase):
    def __init__(self):
        self._portfolio = Portfolio()

        # Track prices over time
        self._prices = {}
        self._trades = {}

        # Track active (open) orders
        self._active_orders = []

        # Track active positions
        self._active_positions = {}

    def _setManager(self, manager):
        """install manager"""
        self._manager = manager

    def newPosition(self, strategy, trade: Trade):
        """create and track a new position, or update the pnl/price of
        an existing position"""
        self._portfolio.newPosition(strategy, trade)

    def updateStrategies(self, strategies: List) -> None:
        """update with list of strategies"""
        self._portfolio.updateStrategies(strategies)

    def updateAccount(self, positions: List[Position]) -> None:
        """update positions tracking with a position from the exchange"""
        self._portfolio.updateAccount(positions)

    def updateCash(self, positions: List[Position]) -> None:
        """update cash positions from exchange"""
        self._portfolio.updateCash(positions)

    # *********************
    # Risk Methods        *
    # *********************
    def portfolio(self):
        return self._portfolio

    def positions(
        self, strategy, instrument: Instrument = None, exchange: ExchangeType = None
    ):
        return self._portfolio.positions(
            strategy=strategy, instrument=instrument, exchange=exchange
        )

    def priceHistory(self, instrument: Instrument = None):
        if instrument:
            return pd.DataFrame(
                self._prices[instrument], columns=[instrument.name, "when"]
            )
        return {
            i: pd.DataFrame(self._prices[i], columns=[i.name, "when"])
            for i in self._prices
        }

    # **********************
    # EventHandler methods *
    # **********************
    async def onTrade(self, event: Event):
        trade: Trade = event.target  # type: ignore
        self._portfolio.onTrade(trade)

    async def onCancel(self, event):
        # TODO
        pass

    async def onOpen(self, event: Event):
        # TODO
        pass

    async def onFill(self, event: Event):
        # TODO
        pass

    async def onChange(self, event: Event):
        # TODO
        pass

    async def onData(self, event: Event):
        # TODO
        pass

    async def onHalt(self, event: Event):
        # TODO
        pass

    async def onContinue(self, event: Event):
        # TODO
        pass

    async def onError(self, event: Event):
        # TODO
        pass

    async def onStart(self, event: Event):
        # TODO
        pass

    async def onExit(self, event: Event):
        # TODO
        pass

    #########################
    # Order Entry Callbacks #
    #########################
    async def onTraded(  # type: ignore[override]
        self, event: Event, strategy: Optional[EventHandler]
    ):
        trade: Trade = event.target  # type: ignore
        self._portfolio.onTraded(trade, strategy)
