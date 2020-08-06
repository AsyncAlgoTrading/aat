from aat import Strategy, Event, Order, Trade, Side, Instrument, InstrumentType


class BuyAndHoldIBStrategy(Strategy):
    def __init__(self, *args, **kwargs) -> None:
        super(BuyAndHoldIBStrategy, self).__init__(*args, **kwargs)

    async def onStart(self, event: Event) -> None:
        # Get available instruments from exchange
        for name in ('MSFT', 'AAPL'):
            # Create an instrument
            inst = Instrument(name=name, type=InstrumentType.EQUITY)
            insts = await self.lookup(inst)

            # Check that its available
            if inst not in insts:
                raise Exception('Not available on exchange: {}'.format(name))

            # Subscribe
            self.subscribe(inst)
            print('Subscribing to {}'.format(inst))

    async def onTrade(self, event: Event) -> None:
        '''Called whenever a `Trade` event is received'''
        trade: Trade = event.target  # type: ignore

        # no past trades, no current orders
        if not self.orders(trade.instrument) and not self.trades(trade.instrument):
            req = Order(side=Side.BUY,
                        price=trade.price,
                        volume=5000 // trade.price,
                        instrument=trade.instrument,
                        order_type=Order.Types.MARKET,
                        exchange=trade.exchange)

            print('requesting buy : {}'.format(req))

            await self.newOrder(req)

    async def onBought(self, event: Event) -> None:
        trade: Trade = event.target  # type: ignore
        print('bought {:.2f} @ {:.2f}'.format(trade.volume, trade.price))

    async def onRejected(self, event: Event) -> None:
        print('order rejected')
        import sys
        sys.exit(0)

    async def onExit(self, event: Event) -> None:
        print('Finishing...')
