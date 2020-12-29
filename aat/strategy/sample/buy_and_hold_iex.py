from typing import Any
from aat import Strategy, Event, Order, Trade, Side, Instrument, InstrumentType


class BuyAndHoldIEXStrategy(Strategy):
    def __init__(self, symbol: str, *args: Any, **kwargs: Any) -> None:
        super(BuyAndHoldIEXStrategy, self).__init__(*args, **kwargs)
        self._symbol = symbol

    async def onStart(self, event: Event) -> None:
        # Create an instrument
        inst = Instrument(name=self._symbol, type=InstrumentType.EQUITY)

        # Check that its available
        if inst not in self.instruments():
            raise Exception("Not available on exchange: {}".format(self._symbol))

        # Subscribe
        await self.subscribe(inst)
        print("Subscribing to {}".format(inst))

    async def onTrade(self, event: Event) -> None:
        """Called whenever a `Trade` event is received"""
        trade: Trade = event.target  # type: ignore

        # no past trades, no current orders
        if not self.orders(trade.instrument) and not self.trades(trade.instrument):
            self._order = Order(
                side=Side.BUY,
                price=trade.price,
                volume=5000 // trade.price,
                instrument=trade.instrument,
                order_type=Order.Types.MARKET,
                exchange=trade.exchange,
            )

            print("requesting buy : {}".format(self._order))

            await self.newOrder(self._order)

    async def onBought(self, event: Event) -> None:
        trade: Trade = event.target  # type: ignore
        print(
            "bought {} {:.2f} @ {:.2f}".format(
                trade.instrument, trade.volume, trade.price
            )
        )
        assert trade.my_order == self._order

    async def onRejected(self, event: Event) -> None:
        print("order rejected")
        import sys

        sys.exit(0)

    async def onExit(self, event: Event) -> None:
        print("Finishing...")
        self.performanceCharts()
