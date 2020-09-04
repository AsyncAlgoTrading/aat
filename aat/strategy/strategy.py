import asyncio
from abc import abstractmethod
from .calculations import CalculationsMixin
from .utils import StrategyUtilsMixin
from ..config import Side
from ..core import Event, EventHandler, Order, Instrument


class Strategy(EventHandler, StrategyUtilsMixin, CalculationsMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return self.__class__.__name__

    #########################
    # Event Handler Methods #
    #########################
    @abstractmethod
    async def onTrade(self, event: Event) -> None:
        '''Called whenever a `Trade` event is received'''

    async def onOrder(self, event: Event) -> None:
        '''Called whenever an Order `Open`, `Cancel`, `Change`, or `Fill` event is received'''
        pass

    async def onOpen(self, event: Event) -> None:
        '''Called whenever an Order `Open` event is received'''
        pass

    async def onCancel(self, event: Event) -> None:
        '''Called whenever an Order `Cancel` event is received'''
        pass

    async def onChange(self, event: Event) -> None:
        '''Called whenever an Order `Change` event is received'''
        pass

    async def onFill(self, event: Event) -> None:
        '''Called whenever an Order `Fill` event is received'''
        pass

    async def onData(self, event: Event) -> None:
        '''Called whenever other data is received'''
        pass

    async def onHalt(self, event: Event) -> None:
        '''Called whenever an exchange `Halt` event is received, i.e. an event to stop trading'''
        pass

    async def onContinue(self, event: Event) -> None:
        '''Called whenever an exchange `Continue` event is received, i.e. an event to continue trading'''
        pass

    async def onError(self, event: Event) -> None:
        '''Called whenever an internal error occurs'''
        pass

    async def onStart(self, event: Event) -> None:
        '''Called once at engine initialization time'''
        pass

    async def onExit(self, event: Event) -> None:
        '''Called once at engine exit time'''
        pass

    #########################
    # Order Entry Callbacks #
    #########################
    async def onBought(self, event: Event):
        '''callback method for if your order executes (buy)

        Args:
            trade (Trade): the trade/s as your order completes
        '''
        pass

    async def onSold(self, event: Event):
        '''callback method for if your order executes (sell)

        Args:
            trade (Trade): the trade/s as your order completes
        '''
        pass

    async def onTraded(self, event: Event):
        '''callback method for if your order executes (either buy or sell)

        Args:
            trade (Trade): the trade/s as your order completes
        '''
        pass

    async def onRejected(self, event: Event):
        '''callback method for if your order fails to execute

        Args:
            order (Order): the order you attempted to make
        '''
        pass

    async def onCanceled(self, event: Event):
        '''callback method for if your order is canceled

        Args:
            order (Order): the order you canceled
        '''
        pass

    #######################
    # Order Entry Methods #
    #######################
    async def newOrder(self, order: Order):
        '''helper method, defers to buy/sell'''
        # defer to execution
        return await self._manager.newOrder(self, order)

    async def cancelOrder(self, order: Order):
        '''cancel an open order

        Args:
            order (Order): an order to submit to the exchange
        Returns:
            None
        '''
        # defer to execution
        return await self._manager.cancelOrder(self, order)

    async def cancel(self, order: Order):
        '''cancel an open order

        Args:
            order (Order): an order to submit to the exchange
        Returns:
            None
        '''
        # defer to execution
        return await self._manager.cancelOrder(self, order)

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

    async def cancelAll(self, instrument: Instrument = None):
        '''cancel all open orders. If argument is provided, cancel only orders for
        that instrument.

        Args:
            insrument (Optional[Instrument]): Cancel all orders that trade this instrument
        Returns:
            None
        '''
        orders = self.orders(instrument=instrument)
        if orders:
            return await asyncio.wait([self.cancel(order) for order in orders])

    async def closeAll(self, instrument: Instrument = None):
        '''close all open postions immediately. If argument is provided, close only positions for
        that instrument.

        Args:
            insrument (Optional[Instrument]): Close all positions for this instrument
        Returns:
            None
        '''
        # cancel all open orders
        await self.cancelAll(instrument=instrument)

        # construct closing orders
        orders = [Order(volume=p.size,
                        price=0,
                        side=Side.SELL if p.size > 0 else Side.BUY,
                        instrument=p.instrument,
                        exchange=p.exchange) for p in self.positions(instrument=instrument) if p.size != 0]
        return await asyncio.wait([self.newOrder(order) for order in orders])


setattr(Strategy.onTrade, '_original', 1)
setattr(Strategy.onOrder, '_original', 1)
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
setattr(Strategy.onTraded, '_original', 1)
