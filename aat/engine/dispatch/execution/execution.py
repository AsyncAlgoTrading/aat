from typing import TYPE_CHECKING, cast, Dict, List, Optional, Tuple

from aat.core import Order, Event, Trade, ExchangeType
from aat.core.handler import EventHandler
from aat.exchange import Exchange
from aat.strategy import Strategy
from ..base import ManagerBase


if TYPE_CHECKING:
    from ..manager import StrategyManager


class OrderManager(ManagerBase):
    def __init__(self) -> None:
        # map exchangetype to exchange instance
        self._exchanges: Dict[ExchangeType, Exchange] = {}

        # track which strategies generated which orders
        self._pending_orders: Dict[str, Tuple[Order, Optional[Strategy]]] = {}

        # past orders
        self._past_orders: List[Order] = []

    def addExchange(self, exchange: Exchange) -> None:
        """add an exchange"""
        self._exchanges[exchange.exchange()] = exchange

    def _setManager(self, manager: "StrategyManager") -> None:  # type: ignore
        """install manager"""
        self._manager = manager

    # *********************
    # Order Entry Methods *
    # *********************
    async def newOrder(self, strategy: Optional[Strategy], order: Order) -> bool:
        exchange = self._exchanges.get(order.exchange)
        if not exchange:
            raise Exception("Exchange not installed: {}".format(order.exchange))

        ret = await exchange.newOrder(order)
        self._pending_orders[order.id] = (order, strategy)
        return ret

    async def cancelOrder(self, strategy: Optional[Strategy], order: Order) -> bool:
        exchange = self._exchanges.get(order.exchange)
        if not exchange:
            raise Exception("Exchange not installed: {}".format(order.exchange))

        ret = await exchange.cancelOrder(order)
        self._pending_orders.pop(order.id, None)
        return ret

    # **********************
    # EventHandler methods *
    # **********************
    async def onTrade(self, event: Event) -> None:
        """Match trade with order"""
        action: bool = False
        strat: Optional[EventHandler] = None
        order: Optional[Order] = None

        trade: Trade = event.target  # type: ignore

        for order in trade.maker_orders:
            if order.id in self._pending_orders:
                action = True
                _, strat = self._pending_orders[order.id]

                # TODO cleaner?
                trade.my_order = order
                trade.id = order.id
                break

        if trade.taker_order.id in self._pending_orders:
            action = True
            order = trade.taker_order

            # TODO cleaner?
            trade.my_order = order
            trade.id = order.id
            _, strat = self._pending_orders[order.id]

        if action:
            if order.side == Order.Sides.SELL:
                # TODO ugly private method
                await self._manager._onSold(
                    cast(Strategy, strat), cast(Trade, event.target)
                )
            else:
                # TODO ugly private method
                await self._manager._onBought(
                    cast(Strategy, strat), cast(Trade, event.target)
                )

            if order.finished():
                del self._pending_orders[order.id]

    async def onCancel(self, event: Event) -> None:
        order: Order = event.target  # type: ignore
        if order.id in self._pending_orders:
            _, strat = self._pending_orders[order.id]

            # TODO ugly private method
            await self._manager._onCanceled(cast(Strategy, strat), order)
            del self._pending_orders[order.id]

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
        self, event: Event, strategy: Optional[EventHandler]
    ) -> None:
        # TODO
        pass

    async def onReceived(  # type: ignore[override]
        self, event: Event, strategy: Optional[EventHandler]
    ) -> None:
        # TODO
        pass

    async def onRejected(  # type: ignore[override]
        self, event: Event, strategy: Optional[EventHandler]
    ) -> None:
        # TODO
        pass

    async def onCanceled(  # type: ignore[override]
        self, event: Event, strategy: Optional[EventHandler]
    ) -> None:
        # TODO
        pass
