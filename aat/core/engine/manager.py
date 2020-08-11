import sys
import traceback

from ..models import Event, Order, Trade
from ..instrument import Instrument
from ..exchange import ExchangeType
from ..handler import EventHandler
from ...config import Side, InstrumentType


class StrategyManager(EventHandler):
    def __init__(self, trading_engine, trading_type, exchanges):
        '''The Manager sits between the strategies and the engine and manages state'''
        # store trading engine
        self._engine = trading_engine

        # store the exchanges
        self._exchanges = exchanges

        # pull from trading engine class
        self._risk_mgr = self._engine.risk_manager
        self._order_mgr = self._engine.order_manager

        # install self for callbacks
        self._risk_mgr._setManager(self)
        self._order_mgr._setManager(self)

        # add exchanges for order manager
        for exc in exchanges:
            self._order_mgr.addExchange(exc)

        # initialize event subscriptions
        self._data_subscriptions = {}

        # initialize order and trade tracking
        self._strategy_open_orders = {}
        self._strategy_past_orders = {}
        self._strategy_trades = {}

        # internal use for synchronizing
        self._alerted_events = {}

    # ********************* #
    # Engine facing methods #
    # ********************* #

    # *********************** #
    # Strategy facing methods #
    # *********************** #
    #####################
    # Order Entry Hooks #
    #####################
    # TODO ugly private method

    async def _onBought(self, strategy, trade: Trade):
        '''callback method for when/if your order executes.

        Args:
            order_or_trade (Union[Order, Trade]): the trade/s as your order completes, and/or a cancellation order
        '''
        # append to list of trades
        self._strategy_trades[strategy].append(trade)

        # push event to loop
        ev = Event(type=Event.Types.BOUGHT, target=trade)
        self._engine.pushTargetedEvent(strategy, ev)

        # synchronize state when engine processes this
        self._alerted_events[ev] = (strategy, trade.my_order)

    # TODO ugly private method
    async def _onSold(self, strategy, trade: Trade):
        '''callback method for when/if your order executes.

        Args:
            order_or_trade (Union[Order, Trade]): the trade/s as your order completes, and/or a cancellation order
        '''
        # append to list of trades
        self._strategy_trades[strategy].append(trade)

        # push event to loop
        ev = Event(type=Event.Types.SOLD, target=trade)
        self._engine.pushTargetedEvent(strategy, ev)

        # synchronize state when engine processes this
        self._alerted_events[ev] = (strategy, trade.my_order)

    # TODO ugly private method

    async def _onRejected(self, strategy, order: Order):
        '''callback method for if your order fails to execute

        Args:
            order (Order): the order you attempted to make
        '''
        # push event to loop
        ev = Event(type=Event.Types.REJECTED, target=order)
        self._engine.pushTargetedEvent(strategy, ev)

        # synchronize state when engine processes this
        self._alerted_events[ev] = (strategy, order)

    # *********************
    # Order Entry Methods *
    # *********************

    async def newOrder(self, strategy, order: Order):
        '''helper method, defers to buy/sell'''
        # ensure has list
        if strategy not in self._strategy_open_orders:
            self._strategy_open_orders[strategy] = []

        if strategy not in self._strategy_past_orders:
            self._strategy_past_orders[strategy] = []

        if strategy not in self._strategy_trades:
            self._strategy_trades[strategy] = []

        # append to open orders list
        self._strategy_open_orders[strategy].append(order)

        # append to past orders list
        self._strategy_past_orders[strategy].append(order)

        # TODO check risk
        ret, approved = await self._risk_mgr.newOrder(strategy, order)

        # was this trade allowed?
        if approved:
            # send to be executed
            await self._order_mgr.newOrder(strategy, order)
            return ret

        # raise onRejected
        self._engine.pushEvent(Event(type=Event.Types.REJECTED, target=order))
        return None

    async def cancelOrder(self, strategy, order: Order):
        '''cancel an open order'''
        await self._order_mgr.cancelOrder(strategy, order)

    def orders(self, strategy, instrument: Instrument = None, exchange: ExchangeType = None, side: Side = None):
        '''select all open orders

        Args:
            instrument (Instrument): filter open orders by instrument
            exchange (ExchangeType): filter open orders by exchange
            side (Side): filter open orders by side
        Returns:
            list (Order): list of open orders
        '''
        # ensure has list
        if strategy not in self._strategy_open_orders:
            self._strategy_open_orders[strategy] = []

        ret = self._strategy_open_orders[strategy].copy()
        if instrument:
            ret = [r for r in ret if r.instrument == instrument]
        if exchange:
            ret = [r for r in ret if r.exchange == exchange]
        if side:
            ret = [r for r in ret if r.side == side]
        return ret

    def pastOrders(self, strategy, instrument: Instrument = None, exchange: ExchangeType = None, side: Side = None):
        '''select all past orders

        Args:
            instrument (Instrument): filter open orders by instrument
            exchange (ExchangeType): filter open orders by exchange
            side (Side): filter open orders by side
        Returns:
            list (Order): list of open orders
        '''
        # ensure has list
        if strategy not in self._strategy_past_orders:
            self._strategy_past_orders[strategy] = []

        ret = self._strategy_past_orders[strategy].copy()
        if instrument:
            ret = [r for r in ret if r.instrument == instrument]
        if exchange:
            ret = [r for r in ret if r.exchange == exchange]
        if side:
            ret = [r for r in ret if r.side == side]
        return ret

    def trades(self, strategy, instrument: Instrument = None, exchange: ExchangeType = None, side: Side = None):
        '''select all past trades

        Args:
            instrument (Instrument): filter trades by instrument
            exchange (ExchangeType): filter trades by exchange
            side (Side): filter trades by side
        Returns:
            list (Trade): list of trades
        '''
        # ensure has list
        if strategy not in self._strategy_trades:
            self._strategy_trades[strategy] = []

        ret = self._strategy_trades[strategy].copy()
        if instrument:
            ret = [r for r in ret if r.instrument == instrument]
        if exchange:
            ret = [r for r in ret if r.exchange == exchange]
        if side:
            ret = [r for r in ret if r.side == side]
        return ret

    # *********************
    # Risk Methods        *
    # *********************
    def positions(self, instrument=None, exchange=None, side=None):
        return self._risk_mgr.positions(instrument=instrument, exchange=exchange, side=side)

    def risk(self, position=None):
        return self._risk_mgr.risk(position=position)

    def priceHistory(self, instrument=None):
        return self._risk_mgr.priceHistory(instrument=instrument)

    # **********************
    # EventHandler methods *
    # **********************
    async def onTrade(self, event):
        await self._risk_mgr.onTrade(event)
        await self._order_mgr.onTrade(event)

    async def onOpen(self, event):
        await self._risk_mgr.onOpen(event)
        await self._order_mgr.onOpen(event)

    async def onCancel(self, event):
        await self._risk_mgr.onCancel(event)
        await self._order_mgr.onCancel(event)

    async def onChange(self, event):
        await self._risk_mgr.onChange(event)
        await self._order_mgr.onChange(event)

    async def onFill(self, event):
        await self._risk_mgr.onFill(event)
        await self._order_mgr.onFill(event)

    async def onHalt(self, event):
        await self._risk_mgr.onHalt(event)
        await self._order_mgr.onHalt(event)

    async def onContinue(self, event):
        await self._risk_mgr.onContinue(event)
        await self._order_mgr.onContinue(event)

    async def onData(self, event):
        # TODO
        await self._risk_mgr.onData(event)
        await self._order_mgr.onData(event)

    async def onError(self, event):
        # TODO
        print('\n\nA Fatal Error has occurred:')
        traceback.print_exception(type(event.target.exception), event.target.exception, event.target.exception.__traceback__)
        sys.exit(1)

    async def onExit(self, event):
        # TODO
        await self._risk_mgr.onExit(event)
        await self._order_mgr.onExit(event)

    async def onStart(self, event):
        # TODO
        await self._risk_mgr.onStart(event)
        await self._order_mgr.onStart(event)

    #########################
    # Order Entry Callbacks #
    #########################
    async def onTraded(self, event: Event):
        # TODO
        await self._risk_mgr.onTraded(event)
        await self._order_mgr.onTraded(event)

        if event in self._alerted_events:
            strategy, order = self._alerted_events[event]
            # remove from list of open orders if done
            if order.filled >= order.volume:
                self._strategy_open_orders[strategy].remove(order)

    async def onRejected(self, event: Event):
        # TODO
        await self._risk_mgr.onRejected(event)
        await self._order_mgr.onRejected(event)

        # synchronize state
        if event in self._alerted_events:
            strategy, order = self._alerted_events[event]
            # remove from list of open orders
            self._strategy_open_orders[strategy].remove(order)

    async def onCanceled(self, event: Event):
        # TODO
        await self._risk_mgr.onCanceled(event)
        await self._order_mgr.onCanceled(event)

        # synchronize state
        if event in self._alerted_events:
            strategy, order = self._alerted_events[event]
            # remove from list of open orders
            self._strategy_open_orders[strategy].remove(order)

    #################
    # Other Methods #
    #################
    def now(self):
        '''Return the current datetime. Useful to avoid code changes between
        live trading and backtesting. Defaults to `datetime.now`'''
        return self._engine.now()

    def instruments(self, type: InstrumentType = None, exchange=None):
        '''Return list of all available instruments'''
        return Instrument._instrumentdb.instruments(type=type, exchange=exchange)

    async def subscribe(self, instrument=None, strategy=None):
        '''Subscribe to market data for the given instrument'''
        if strategy not in self._data_subscriptions:
            self._data_subscriptions[strategy] = []

        self._data_subscriptions[strategy].append(instrument)

        for exc in self._exchanges:
            await exc.subscribe(instrument)

    def dataSubscriptions(self, handler, event):
        '''does handler subscribe to the data for event'''
        if handler not in self._data_subscriptions:
            # subscribe all by default
            return True
        return event.target.instrument in self._data_subscriptions[handler]

    async def lookup(self, instrument: Instrument, exchange=None):
        '''Return list of all available instruments that match the instrument given'''
        if exchange in self._exchanges:
            return await self._exchanges.lookup(instrument)
        elif exchange is None:
            ret = []
            for exchange in self._exchanges:
                ret.extend(await exchange.lookup(instrument))
            return ret

        # None implement
        raise NotImplementedError()
