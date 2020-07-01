from abc import abstractmethod
from typing import Union
from ..config import Side
from ..core import Event, EventHandler, Trade, Order, Instrument, ExchangeType


class Strategy(EventHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #########################
    # Event Handler Methods #
    #########################
    @abstractmethod
    async def onTrade(self, event: Event):
        '''Called whenever a `Trade` event is received'''

    async def onOpen(self, event: Event):
        '''Called whenever an Order `Open` event is received'''
        pass

    async def onCancel(self, event: Event):
        '''Called whenever an Order `Cancel` event is received'''
        pass

    async def onChange(self, event: Event):
        '''Called whenever an Order `Change` event is received'''
        pass

    async def onFill(self, event: Event):
        '''Called whenever an Order `Fill` event is received'''
        pass

    async def onData(self, event: Event):
        '''Called whenever other data is received'''
        pass

    async def onHalt(self, data):
        '''Called whenever an exchange `Halt` event is received, i.e. an event to stop trading'''
        pass

    async def onContinue(self, data):
        '''Called whenever an exchange `Continue` event is received, i.e. an event to continue trading'''
        pass

    async def onError(self, event: Event):
        '''Called whenever an internal error occurs'''
        pass

    async def onStart(self):
        '''Called once at engine initialization time'''
        pass

    async def onExit(self):
        '''Called once at engine exit time'''
        pass

    #########################
    # Order Entry Callbacks #
    #########################
    async def onBought(self, trade: Trade):
        '''callback method for if your order executes.

        Args:
            trade (Trade): the trade/s as your order completes
        '''
        pass

    async def onSold(self, trade: Trade = None):
        '''callback method for if your order executes.

        Args:
            trade (Trade): the trade/s as your order completes
        '''
        pass

    async def onRejected(self, order: Order):
        '''callback method for if your order fails to execute

        Args:
            order (Order): the order you attempted to make
        '''
        pass

    #######################
    # Order Entry Methods #
    #######################
    async def newOrder(self, order: Order):
        '''helper method, defers to buy/sell'''
        # defer to execution
        return await self._manager.newOrder(self, order)

    async def buy(self, order: Order):
        '''submit a buy order. Note that this is merely a request for an order, it provides no guarantees that the order will
        execute. At a later point, if your order executes, you will receive an alert via the `bought` method

        Args:
            order (Order): an order to submit to the exchange
        Returns:
            None
        '''
        return await self._manager.newOrder(self, order)

    async def sell(self, order: Order):
        '''submit a sell order. Note that this is merely a request for an order, it provides no guarantees that the order will
        execute. At a later point, if your order executes, you will receive an alert via the `sold` method

        Args:
            order (Order): an order to submit to the exchange
        Returns:
            None
        '''
        return await self._manager.newOrder(self, order)


    def orders(self, instrument: Instrument = None, exchange: ExchangeType = None, side: Side = None):
        '''select all open orders

        Args:
            instrument (Instrument): filter open orders by instrument
            exchange (ExchangeType): filter open orders by exchange
            side (Side): filter open orders by side
        Returns:
            list (Order): list of open orders
        ''' 
        return self._manager.orders(self, instrument, exchange, side)

    def pastOrders(self, instrument: Instrument = None, exchange: ExchangeType = None, side: Side = None):
        '''select all past orders

        Args:
            instrument (Instrument): filter open orders by instrument
            exchange (ExchangeType): filter open orders by exchange
            side (Side): filter open orders by side
        Returns:
            list (Order): list of open orders
        '''
        return self._manager.pastOrders(self, instrument, exchange, side)

    def trades(self, instrument: Instrument = None, exchange: ExchangeType = None, side: Side = None):
        '''select all past trades

        Args:
            instrument (Instrument): filter trades by instrument
            exchange (ExchangeType): filter trades by exchange
            side (Side): filter trades by side
        Returns:
            list (Trade): list of trades
        '''
        return self._manager.trades(self, instrument, exchange, side)

    ################
    # Risk Methods #
    ################
    def positions(self, instrument: Instrument = None, exchange: ExchangeType = None, side: Side = None):
        '''select all positions

        Args:
            instrument (Instrument): filter positions by instrument
            exchange (ExchangeType): filter positions by exchange
            side (Side): filter positions by side
        Returns:
            list (Position): list of positions
        '''
        # TODO move me to manager
        return self._manager.positions(instrument=instrument, exchange=exchange, side=side)

    def risk(self, position=None):
        '''Get risk metrics 

        Args:
            position (Position): only get metrics on this position
        Returns:
            dict: metrics
        '''
        # TODO move me to manager
        return self._manager.risk(position=position)

    #################
    # Other Methods #
    #################
    async def onAnalyze(self, engine):
        '''Called once after engine exit to analyze the results of a backtest'''
        pass

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
setattr(Strategy.onCancel, '_original', 1)
setattr(Strategy.onChange, '_original', 1)
setattr(Strategy.onFill, '_original', 1)
setattr(Strategy.onData, '_original', 1)
setattr(Strategy.onHalt, '_original', 1)
setattr(Strategy.onContinue, '_original', 1)
setattr(Strategy.onError, '_original', 1)
setattr(Strategy.onStart, '_original', 1)
setattr(Strategy.onExit, '_original', 1)

setattr(Strategy.onBought, '_original', 1)
setattr(Strategy.onSold, '_original', 1)
setattr(Strategy.onRejected, '_original', 1)

setattr(Strategy.onAnalyze, '_original', 1)