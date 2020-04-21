from abc import abstractmethod
from typing import Union
from ..config import Side
from ..core import Event, EventHandler, Trade, Order, Instrument, ExchangeType


class Strategy(EventHandler):
    def __init__(self, *args, **kwargs):
        self._strategy_open_orders = []
        self._strategy_past_orders = []
        self._strategy_trades = []

    #########################
    # Event Handler Methods #
    #########################
    @abstractmethod
    def onTrade(self, event: Event):
        '''Called whenever a `Trade` event is received'''

    def onOpen(self, event: Event):
        '''Called whenever an Order `Open` event is received'''
        pass

    def onFill(self, event: Event):
        '''Called whenever an Order `Fill` event is received'''
        pass

    def onCancel(self, event: Event):
        '''Called whenever an Order `Cancel` event is received'''
        pass

    def onChange(self, event: Event):
        '''Called whenever an Order `Change` event is received'''
        pass

    def onError(self, event: Event):
        '''Called whenever an internal error occurs'''
        pass

    def onStart(self):
        '''Called once at engine initialization time'''
        pass

    def onExit(self):
        '''Called once at engine exit time'''
        pass

    def onHalt(self, data):
        '''Called whenever an exchange `Halt` event is received, i.e. an event to stop trading'''
        pass

    def onContinue(self, data):
        '''Called whenever an exchange `Continue` event is received, i.e. an event to continue trading'''
        pass

    def onData(self, event: Event):
        '''Called whenever other data is received'''
        pass

    def onAnalyze(self, engine):
        '''Called once after engine exit to analyze the results of a backtest'''
        pass

    #######################
    # Order Entry Methods #
    #######################
    def newOrder(self, order: Order):
        '''helper method, defers to buy/sell'''
        self._strategy_open_orders.append(order)
        self._manager.newOrder(order, self)

    def buy(self, order: Order):
        '''submit a buy order. Note that this is merely a request for an order, it provides no guarantees that the order will
        execute. At a later point, if your order executes, you will receive an alert via the `bought` method

        Args:
            order (Order): an order to submit to the exchange
        Returns:
            None
        '''
        # TODO move me
        self._strategy_open_orders.append(order)
        self._manager.newOrder(order, self)

    def sell(self, order: Order):
        '''submit a sell order. Note that this is merely a request for an order, it provides no guarantees that the order will
        execute. At a later point, if your order executes, you will receive an alert via the `sold` method

        Args:
            order (Order): an order to submit to the exchange
        Returns:
            None
        '''
        # TODO move me
        self._strategy_open_orders.append(order)
        self._manager.newOrder(order, self)

    def onBought(self, order_or_trade: Union[Order, Trade], my_order: Order = None):
        '''callback method for when/if your order executes.

        Args:
            order_or_trade (Union[Order, Trade]): the trade/s as your order completes, and/or a cancellation order
        '''
        # TODO move me
        self._strategy_trades.append(order_or_trade)

    def onSold(self, order_or_trade: Union[Order, Trade] = None, my_order: Order = None):
        '''callback method for when/if your order executes.

        Args:
            order_or_trade (Union[Order, Trade]): the trade/s as your order completes, and/or a cancellation order
        '''
        # TODO move me
        self._strategy_trades.append(order_or_trade)

    def onReject(self, order: Order):
        '''callback method for if your order fails to execute

        Args:
            order (Order): the order you attempted to make
        '''
        self._strategy_open_orders.remove(order)

    def orders(self, instrument: Instrument = None, exchange: ExchangeType = None, side: Side = None):
        ret = self._strategy_open_orders.copy()
        if instrument:
            ret = [r for r in ret if r.instrument == instrument]
        if exchange:
            ret = [r for r in ret if r.exchange == exchange]
        if side:
            ret = [r for r in ret if r.side == side]
        return ret

    def pastOrders(self, instrument: Instrument = None, exchange: ExchangeType = None, side: Side = None):
        ret = self._strategy_past_orders.copy()
        if instrument:
            ret = [r for r in ret if r.instrument == instrument]
        if exchange:
            ret = [r for r in ret if r.exchange == exchange]
        if side:
            ret = [r for r in ret if r.side == side]
        return ret

    def trades(self, instrument: Instrument = None, exchange: ExchangeType = None, side: Side = None):
        ret = self._strategy_trades.copy()
        if instrument:
            ret = [r for r in ret if r.instrument == instrument]
        if exchange:
            ret = [r for r in ret if r.exchange == exchange]
        if side:
            ret = [r for r in ret if r.side == side]
        return ret

    #################
    # Other Methods #
    #################

    def slippage(self, trade: Trade):
        '''method to inject slippage when backtesting

        Args:
            trade (Trade): the completed trade to adjust
        Returns:
            trade (Trade): the modified trade
        '''
        pass

    def transactionCost(self, trade: Trade):
        '''method to inject transaction costs when backtesting

        Args:
            trade (Trade): the completed trade to adjust
        Returns:
            trade (Trade): the modified trade
        '''
        pass


setattr(Strategy.onTrade, '_original', 1)
setattr(Strategy.onOpen, '_original', 1)
setattr(Strategy.onFill, '_original', 1)
setattr(Strategy.onCancel, '_original', 1)
setattr(Strategy.onChange, '_original', 1)
setattr(Strategy.onError, '_original', 1)
setattr(Strategy.onStart, '_original', 1)
setattr(Strategy.onExit, '_original', 1)
setattr(Strategy.onHalt, '_original', 1)
setattr(Strategy.onContinue, '_original', 1)
setattr(Strategy.onData, '_original', 1)
setattr(Strategy.onAnalyze, '_original', 1)
