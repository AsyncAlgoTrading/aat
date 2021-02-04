from typing import TYPE_CHECKING, cast, Dict, List, Optional, Tuple

from aat.core import Order, Event, Trade, ExchangeType
from aat.core.handler import EventHandler
from aat.exchange import Exchange
from ..base import ManagerBase


if TYPE_CHECKING:
    from aat.strategy import Strategy
    from ..manager import StrategyManager


class OrderManager(ManagerBase):
    def __init__(self) -> None:
        # map exchangetype to exchange instance
        self._exchanges: Dict[ExchangeType, Exchange] = {}

        # track which strategies generated which orders
        self._pending_orders: Dict[str, Tuple[Order, Optional["Strategy"]]] = {}

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
    async def newOrder(self, strategy: Optional["Strategy"], order: Order) -> bool:
        exchange = self._exchanges.get(order.exchange)
        if not exchange:
            raise Exception("Exchange not installed: {}".format(order.exchange))

        ret = await exchange.newOrder(order)
        if ret:
            print("putting into pending")
            self._pending_orders[order.id] = (order, strategy)
        return ret

    async def cancelOrder(self, strategy: Optional["Strategy"], order: Order) -> bool:
        exchange = self._exchanges.get(order.exchange)
        if not exchange:
            raise Exception("Exchange not installed: {}".format(order.exchange))

        ret = await exchange.cancelOrder(order)
        if ret:
            self._pending_orders.pop(order.id, None)
        return ret

    # **********************
    # EventHandler methods *
    # **********************
    async def onTrade(self, event: Event) -> None:
        """Match trade with order"""
        action: bool = False
        strat: Optional[EventHandler] = None

        trade: Trade = event.target

        # if it comes with the order, use that
        if trade.my_order:
            action = True
            order, strat = self._pending_orders[trade.my_order.id]

            # TODO cleaner?
            trade.id = trade.my_order.id

        # otherwise derive from mapping
        else:
            for maker_order in trade.maker_orders:
                if maker_order.id in self._pending_orders:
                    action = True
                    order, strat = self._pending_orders[maker_order.id]

                    # TODO cleaner?
                    trade.my_order = order
                    trade.id = order.id
                    order.filled = maker_order.filled
                    break

            if trade.taker_order.id in self._pending_orders:
                action = True
                order, strat = self._pending_orders[trade.taker_order.id]

                # TODO cleaner?
                trade.my_order = order
                trade.id = order.id
                order.filled = trade.taker_order.filled

        if action:
            if order.side == Order.Sides.SELL:
                # TODO ugly private method
                await self._manager._onSold(
                    cast("Strategy", strat), cast(Trade, event.target)
                )
            else:
                # TODO ugly private method
                await self._manager._onBought(
                    cast("Strategy", strat), cast(Trade, event.target)
                )

            if order.finished():
                del self._pending_orders[order.id]

    async def onCancel(self, event: Event) -> None:
        canceled_order: Order = event.target
        if canceled_order.id in self._pending_orders:
            order, strat = self._pending_orders[canceled_order.id]

            # TODO second look, just in case
            order.filled = canceled_order.filled

            # TODO ugly private method
            await self._manager._onCanceled(cast("Strategy", strat), order)
            del self._pending_orders[canceled_order.id]

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
