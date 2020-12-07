import sys
import traceback

from typing import cast, List, TYPE_CHECKING

from .order_entry import StrategyManagerOrderEntryMixin, OrderManager
from .periodic import PeriodicManagerMixin
from .portfolio import StrategyManagerPortfolioMixin, PortfolioManager
from .risk import StrategyManagerRiskMixin, RiskManager
from .utils import StrategyManagerUtilsMixin

from aat.config import TradingType
from aat.core import Event, Error
from aat.exchange import Exchange
from aat.core.handler import EventHandler
from aat.strategy import Strategy

if TYPE_CHECKING:
    from aat.engine import TradingEngine


class StrategyManager(
    StrategyManagerOrderEntryMixin,
    StrategyManagerRiskMixin,
    StrategyManagerPortfolioMixin,
    StrategyManagerUtilsMixin,
    PeriodicManagerMixin,
    EventHandler,
):
    def __init__(
        self,
        trading_engine: "TradingEngine",
        trading_type: TradingType,
        exchanges: List[Exchange],
        load_accounts: bool = False,
    ) -> None:
        """The Manager sits between the strategies and the engine and manages state

        Args:
            trading_engine (TradingEngine); the trading engine instance
            trading_type (TradingType); the trading type
            exchanges (List[Exchange]); a list of exchanges to dispatch to
            load_accounts (bool); load positions from accounts on startup
        """

        # store trading engine
        self._engine = trading_engine

        # store the exchanges
        self._exchanges = exchanges

        # store whether to query accounts on start
        self._load_accounts = load_accounts

        # pull from trading engine class
        self._portfolio_mgr = self._engine.portfolio_manager
        self._risk_mgr = self._engine.risk_manager
        self._order_mgr = self._engine.order_manager

        # install self for callbacks
        self._portfolio_mgr._setManager(self)
        self._risk_mgr._setManager(self)
        self._order_mgr._setManager(self)

        # add exchanges for order manager
        for exc in exchanges:
            self._order_mgr.addExchange(exc)

        # initialize event subscriptions
        self._data_subscriptions = {}  # type: ignore

        # initialize order and trade tracking
        self._strategy_open_orders = {}
        self._strategy_past_orders = {}
        self._strategy_trades = {}

        # internal use for synchronizing
        self._alerted_events = {}

        # internal use for periodics
        self._periodics = []

    # ********* #
    # Accessors #
    # ********* #
    def riskManager(self) -> RiskManager:
        return self._risk_mgr

    def orderManager(self) -> OrderManager:
        return self._order_mgr

    def portfolioManager(self) -> PortfolioManager:
        return self._portfolio_mgr

    def strategies(self) -> List[Strategy]:
        return self._engine.strategies

    def exchanges(self) -> List[Exchange]:
        return self._engine.exchanges

    # ********************* #
    # EventHandler methods *
    # **********************
    async def onTrade(self, event: Event) -> None:
        await self._portfolio_mgr.onTrade(event)
        await self._risk_mgr.onTrade(event)
        await self._order_mgr.onTrade(event)

    async def onOpen(self, event: Event) -> None:
        await self._portfolio_mgr.onOpen(event)
        await self._risk_mgr.onOpen(event)
        await self._order_mgr.onOpen(event)

    async def onCancel(self, event: Event) -> None:
        await self._portfolio_mgr.onCancel(event)
        await self._risk_mgr.onCancel(event)
        await self._order_mgr.onCancel(event)

    async def onChange(self, event: Event) -> None:
        await self._portfolio_mgr.onChange(event)
        await self._risk_mgr.onChange(event)
        await self._order_mgr.onChange(event)

    async def onFill(self, event: Event) -> None:
        await self._portfolio_mgr.onFill(event)
        await self._risk_mgr.onFill(event)
        await self._order_mgr.onFill(event)

    async def onHalt(self, event: Event) -> None:
        await self._portfolio_mgr.onHalt(event)
        await self._risk_mgr.onHalt(event)
        await self._order_mgr.onHalt(event)

    async def onContinue(self, event: Event) -> None:
        await self._portfolio_mgr.onContinue(event)
        await self._risk_mgr.onContinue(event)
        await self._order_mgr.onContinue(event)

    async def onData(self, event: Event) -> None:
        await self._portfolio_mgr.onData(event)
        await self._risk_mgr.onData(event)
        await self._order_mgr.onData(event)

    async def onError(self, event: Event) -> None:
        print("\n\nA Fatal Error has occurred:")
        error = cast(Error, event.target)
        traceback.print_exception(
            type(error.exception),
            error.exception,
            error.exception.__traceback__,
        )
        sys.exit(1)

    async def onExit(self, event: Event) -> None:
        await self._portfolio_mgr.onExit(event)
        await self._risk_mgr.onExit(event)
        await self._order_mgr.onExit(event)

    async def onStart(self, event: Event) -> None:
        # Initialize strategies
        self._portfolio_mgr.updateStrategies(self.strategies())

        # Initialize positions
        for exchange in self.exchanges():
            if self._load_accounts:
                acc = await exchange.accounts()
                self._portfolio_mgr.updateAccount(acc)

            acc = await exchange.balance()
            self._portfolio_mgr.updateCash(acc)
            self._risk_mgr.updateCash(acc)

        # Defer to sub onStarts
        await self._portfolio_mgr.onStart(event)
        await self._risk_mgr.onStart(event)
        await self._order_mgr.onStart(event)
