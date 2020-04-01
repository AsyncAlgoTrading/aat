from abc import abstractmethod
from typing import Union
from ..core import Event, EventHandler, Trade, Order


class Strategy(EventHandler):
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
    def buy(self, order: Order):
        '''submit a buy order. Note that this is merely a request for an order, it provides no guarantees that the order will
        execute. At a later point, if your order executes, you will receive an alert via the `bought` method

        Args:
            order (Order): an order to submit to the exchange
        Returns:
            None
        '''
        pass

    def sell(self):
        '''submit a sell order. Note that this is merely a request for an order, it provides no guarantees that the order will
        execute. At a later point, if your order executes, you will receive an alert via the `sold` method

        Args:
            order (Order): an order to submit to the exchange
        Returns:
            None
        '''
        pass

    def bought(self, order_or_trade: Union[Order, Trade]):
        '''callback method for when/if your order executes.

        Args:
            order_or_trade (Union[Order, Trade]): the trade/s as your order completes, and/or a cancellation order
        '''
        pass

    def sold(self, order_or_trade: Union[Order, Trade]):
        '''callback method for when/if your order executes.

        Args:
            order_or_trade (Union[Order, Trade]): the trade/s as your order completes, and/or a cancellation order
        '''
        pass

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


Strategy.onTrade._original = 1
Strategy.onOpen._original = 1
Strategy.onFill._original = 1
Strategy.onCancel._original = 1
Strategy.onChange._original = 1
Strategy.onError._original = 1
Strategy.onStart._original = 1
Strategy.onExit._original = 1
Strategy.onHalt._original = 1
Strategy.onContinue._original = 1
Strategy.onData._original = 1
Strategy.onAnalyze._original = 1
