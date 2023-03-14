import pandas as pd  # type: ignore
from datetime import datetime
from typing import cast, Dict, List, Optional, Tuple, Union, TYPE_CHECKING

from aat.core import Event, Trade, Instrument, ExchangeType, Position

from ..base import ManagerBase
from .portfolio import Portfolio


if TYPE_CHECKING:
    from aat.strategy import Strategy
    from ..manager import StrategyManager


class PortfolioManager(ManagerBase):
    def __init__(self) -> None:
        self._portfolio = Portfolio()

        # Track prices over time
        self._prices: Dict[Instrument, List[Tuple[datetime, float]]] = {}
        self._trades = {}  # type: ignore

        # Track active (open) orders
        self._active_orders = []  # type: ignore

        # Track active positions
        self._active_positions = {}  # type: ignore

    def _setManager(self, manager: "StrategyManager") -> None:
        """install manager"""
        self._manager = manager

    def newPosition(self, trade: Trade, strategy: "Strategy") -> None:
        """create and track a new position, or update the pnl/price of
        an existing position"""
        self._portfolio.newPosition(trade, strategy)

    def updateStrategies(self, strategies: List["Strategy"]) -> None:
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
    def portfolio(self) -> Portfolio:
        return self._portfolio

    def positions(
        self,
        strategy: "Strategy",
        instrument: Optional[Instrument] = None,
        exchange: Optional[ExchangeType] = None,
    ) -> List[Position]:
        return self._portfolio.positions(
            strategy=strategy, instrument=instrument, exchange=exchange
        )

    def priceHistory(
        self, instrument: Optional[Instrument] = None
    ) -> Union[dict, pd.DataFrame]:
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
    async def onTrade(self, event: Event) -> None:
        trade: Trade = event.target  # type: ignore
        self._portfolio.onTrade(trade)

    async def onCancel(self, event: Event) -> None:
        # TODO
        pass

    async def onOpen(self, event: Event) -> None:
        # TODO
        pass

    async def onFill(self, event: Event) -> None:
        # TODO
        pass

    async def onChange(self, event: Event) -> None:
        # TODO
        pass

    async def onData(self, event: Event) -> None:
        # TODO
        pass

    async def onHalt(self, event: Event) -> None:
        # TODO
        pass

    async def onContinue(self, event: Event) -> None:
        # TODO
        pass

    async def onError(self, event: Event) -> None:
        # TODO
        pass

    async def onStart(self, event: Event) -> None:
        # TODO
        pass

    async def onExit(self, event: Event) -> None:
        # TODO
        pass

    #########################
    # Order Entry Callbacks #
    #########################
    async def onTraded(  # type: ignore[override]
        self, event: Event, strategy: Optional["Strategy"]
    ) -> None:
        self._portfolio.onTraded(cast(Trade, event.target), cast("Strategy", strategy))
