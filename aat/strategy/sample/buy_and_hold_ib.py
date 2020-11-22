from aat import Strategy, Event, Order, Trade, Side, Instrument, InstrumentType


class BuyAndHoldIBStrategy(Strategy):
    def __init__(self, instrument, notional, *args, **kwargs) -> None:
        super(BuyAndHoldIBStrategy, self).__init__(*args, **kwargs)

        # symbol to trade
        self._symbol, self._symbol_type = instrument.split("-")

        # notional value to trade
        self._notional = float(notional)

    async def onStart(self, event: Event) -> None:
        # Create an instrument
        inst = Instrument(name=self._symbol, type=InstrumentType(self._symbol_type))

        # Subscribe
        await self.subscribe(inst)
        print("Subscribing to {}".format(inst))

    async def onTrade(self, event: Event) -> None:
        """Called whenever a `Trade` event is received"""
        trade: Trade = event.target  # type: ignore

        # no past trades, no current orders
        if not self.orders(trade.instrument) and not self.trades(trade.instrument):
            req = Order(
                side=Side.BUY,
                price=trade.price,
                volume=self._notional // trade.price,
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
