from aat import Strategy, Event, Order, Trade, Side


class BuyAndHoldStrategy(Strategy):
    def __init__(self, *args, **kwargs) -> None:
        super(BuyAndHoldStrategy, self).__init__(*args, **kwargs)

    async def onStart(self, event: Event) -> None:
        self.subscribe(self.instruments()[0])

    async def onTrade(self, event: Event) -> None:
        '''Called whenever a `Trade` event is received'''
        print('Trade:\n{}'.format(event))

        trade: Trade = event.target  # type: ignore

        # no past trades, no current orders
        if not self.orders(trade.instrument) and not self.trades(trade.instrument):
            req = Order(side=Side.BUY,
                        price=trade.price + 10,
                        volume=1,
                        instrument=trade.instrument,
                        order_type=Order.Types.MARKET,
                        exchange=trade.exchange)

            print("requesting buy : {}".format(req))

            await self.newOrder(req)

        else:
            print(self.positions())
            print(self.risk())

    async def onBought(self, event: Event) -> None:
        trade: Trade = event.target  # type: ignore
        print('bought {:.2f} @ {:.2f}'.format(trade.volume, trade.price))

    async def onReject(self, event: Event) -> None:
        print('order rejected')
        import sys
        sys.exit(0)

    def slippage(self, trade: Trade) -> Trade:
        # trade.slippage = trade.price * .0001  # .01% price impact TODO
        return trade

    def transactionCost(self, trade: Trade) -> Trade:
        # trade.transactionCost = trade.price * trade.volume * .0025  # 0.0025 max fee TODO
        return trade

    async def onExit(self, event: Event) -> None:
        print('Finishing...')
        import matplotlib.pyplot as plt  # type: ignore
        plt.plot(self.positions()[0].unrealizedPnlHistory)
        plt.show()
