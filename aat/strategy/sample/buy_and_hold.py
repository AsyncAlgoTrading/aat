from aat import Strategy, Event, Order, Trade, Side


class BuyAndHoldStrategy(Strategy):
    def __init__(self, *args, **kwargs) -> None:
        super(BuyAndHoldStrategy, self).__init__(*args, **kwargs)

    async def onStart(self, event: Event) -> None:
        await self.subscribe(self.instruments()[0])

    async def onTrade(self, event: Event) -> None:
        """Called whenever a `Trade` event is received"""
        trade: Trade = event.target  # type: ignore

        # no past trades, no current orders
        if not self.orders(trade.instrument) and not self.trades(trade.instrument):
            req = Order(
                side=Side.BUY,
                price=trade.price + 10,
                volume=1.1,
                instrument=trade.instrument,
                order_type=Order.Types.MARKET,
                exchange=trade.exchange,
            )

            print("requesting buy : {}".format(req))

            await self.newOrder(req)

    async def onBought(self, event: Event) -> None:
        trade: Trade = event.target  # type: ignore
        print("bought {:.2f} @ {:.2f}".format(trade.volume, trade.price))

    async def onRejected(self, event: Event) -> None:
        print("order rejected")
        import sys

        sys.exit(0)

    async def onExit(self, event: Event) -> None:
        print("Finishing...")
