from aat import Strategy, Event, Order, Trade, Side


class SellPlusPercentStrategy(Strategy):
    def __init__(self, percent=10, *args, **kwargs) -> None:
        super(SellPlusPercentStrategy, self).__init__(*args, **kwargs)
        self._percent = 1.0 + float(percent) / 100
        self._stop = None

    async def onStart(self, event: Event) -> None:
        self.subscribe(self.instruments()[0])

    async def onTrade(self, event: Event) -> None:
        '''Called whenever a `Trade` event is received'''
        trade: Trade = event.target  # type: ignore

        # no current orders, no past trades
        if not self.orders(trade.instrument) and not self.trades(trade.instrument):
            # import pdb; pdb.set_trace()
            req = Order(side=Side.BUY,
                        price=trade.price,
                        volume=1,
                        instrument=trade.instrument,
                        order_type=Order.Types.MARKET,
                        exchange=trade.exchange)

            print("requesting buy : {}".format(req))
            await self.newOrder(req)

        else:
            # no current orders, 1 past trades, and stop set
            if not self.orders(trade.instrument) and len(self.trades(trade.instrument)) == 1 and \
                    self._stop and trade.price >= self._stop:
                req = Order(side=Side.SELL,
                            price=trade.price,
                            volume=1,
                            instrument=trade.instrument,
                            order_type=Order.Types.MARKET,
                            exchange=trade.exchange)

                print("requesting sell : {}".format(req))

                await self.newOrder(req)

    async def onBought(self, event: Event) -> None:
        trade: Trade = event.target  # type: ignore
        print('bought {:.2f} @ {:.2f}'.format(trade.volume, trade.price))
        self._stop = trade.price * self._percent

    async def onSold(self, event: Event) -> None:
        trade: Trade = event.target  # type: ignore
        print('sold {:.2f} @ {:.2f}'.format(trade.volume, trade.price))
        self._stop = None

    async def onRejected(self, event: Event) -> None:
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
        import pandas as pd  # type: ignore

        position = self.positions()[0]
        price_col = "price - {}".format(position.instrument)
        price_history = pd.DataFrame(position.instrumentPriceHistory, columns=[price_col, "when"])
        price_history.set_index("when", inplace=True)

        unrealized_pnl_history = pd.DataFrame(self.positions()[0].unrealizedPnlHistory, columns=["unrealized_pnl", "when"])
        unrealized_pnl_history.set_index("when", inplace=True)

        realized_pnl_history = pd.DataFrame(self.positions()[0].pnlHistory, columns=["realized_pnl", "when"])
        realized_pnl_history.set_index("when", inplace=True)

        df = pd.concat([price_history, unrealized_pnl_history, realized_pnl_history], axis=1)

        fig, axes = plt.subplots(2, 1)

        df[[price_col]].plot(ax=axes[0], color="grey")
        df[["unrealized_pnl", "realized_pnl"]].plot(ax=axes[1])
        plt.show()
