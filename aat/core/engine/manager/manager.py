import sys
import traceback

from typing import List

from .order_entry import StrategyManagerOrderEntryMixin
from .risk import StrategyManagerRiskMixin
from .utils import StrategyManagerUtilsMixin

from aat.core.handler import EventHandler
from aat.exchange import Exchange


class StrategyManager(StrategyManagerOrderEntryMixin, StrategyManagerRiskMixin, StrategyManagerUtilsMixin, EventHandler):
    def __init__(self, trading_engine, trading_type, exchanges: List[Exchange]):
        '''The Manager sits between the strategies and the engine and manages state'''
        # store trading engine
        self._engine = trading_engine

        # store the exchanges
        self._exchanges = exchanges

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
    def riskManager(self):
        return self._risk_mgr
    
    def orderManager(self):
        return self._order_mgr

    def portfolioManager(self):
        return self._portfolio_mgr

    # ********************* #
    # EventHandler methods *
    # **********************
    async def onTrade(self, event):
        await self._portfolio_mgr.onTrade(event)
        await self._risk_mgr.onTrade(event)
        await self._order_mgr.onTrade(event)

    async def onOpen(self, event):
        await self._portfolio_mgr.onOpen(event)
        await self._risk_mgr.onOpen(event)
        await self._order_mgr.onOpen(event)

    async def onCancel(self, event):
        await self._portfolio_mgr.onCancel(event)
        await self._risk_mgr.onCancel(event)
        await self._order_mgr.onCancel(event)

    async def onChange(self, event):
        await self._portfolio_mgr.onChange(event)
        await self._risk_mgr.onChange(event)
        await self._order_mgr.onChange(event)

    async def onFill(self, event):
        await self._portfolio_mgr.onFill(event)
        await self._risk_mgr.onFill(event)
        await self._order_mgr.onFill(event)

    async def onHalt(self, event):
        await self._portfolio_mgr.onHalt(event)
        await self._risk_mgr.onHalt(event)
        await self._order_mgr.onHalt(event)

    async def onContinue(self, event):
        await self._portfolio_mgr.onContinue(event)
        await self._risk_mgr.onContinue(event)
        await self._order_mgr.onContinue(event)

    async def onData(self, event):
        # TODO
        await self._portfolio_mgr.onData(event)
        await self._risk_mgr.onData(event)
        await self._order_mgr.onData(event)

    async def onError(self, event):
        # TODO
        print('\n\nA Fatal Error has occurred:')
        traceback.print_exception(type(event.target.exception), event.target.exception, event.target.exception.__traceback__)
        sys.exit(1)

    async def onExit(self, event):
        # TODO
        await self._portfolio_mgr.onExit(event)
        await self._risk_mgr.onExit(event)
        await self._order_mgr.onExit(event)

    async def onStart(self, event):
        # TODO
        await self._portfolio_mgr.onStart(event)
        await self._risk_mgr.onStart(event)
        await self._order_mgr.onStart(event)
