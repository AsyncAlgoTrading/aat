import math
from aat import Strategy, Event, Order, Trade, Side


class SellPlusPercentStrategy(Strategy):
    def __init__(self, percent=10, *args, **kwargs) -> None:
        super(SellPlusPercentStrategy, self).__init__(*args, **kwargs)

        self._percent = 1.0 + float(percent) / 100
        self._stop = {}

    async def onTrade(self, event: Event) -> None:
        '''Called whenever a `Trade` event is received'''
        trade: Trade = event.target  # type: ignore

        # no current orders, no past trades
        if not self.orders(trade.instrument) and not self.trades(trade.instrument):
            # import pdb; pdb.set_trace()
            req = Order(side=Side.BUY,
                        price=trade.price,
                        volume=math.ceil(1000 / trade.price),
                        instrument=trade.instrument,
                        order_type=Order.Types.MARKET,
                        exchange=trade.exchange)

            print('requesting buy : {}'.format(req))
            await self.newOrder(req)

        else:
            # no current orders, 1 past trades, and stop set
            if not self.orders(trade.instrument) and len(self.trades(trade.instrument)) == 1 and \
                    trade.instrument in self._stop and trade.price >= self._stop[trade.instrument][0]:
                req = Order(side=Side.SELL,
                            price=trade.price,
                            volume=self._stop[trade.instrument][1],
                            instrument=trade.instrument,
                            order_type=Order.Types.MARKET,
                            exchange=trade.exchange)

                print('requesting sell : {}'.format(req))
                await self.newOrder(req)

    async def onBought(self, event: Event) -> None:
        trade: Trade = event.target  # type: ignore
        print('bought {:.2f} @ {:.2f}'.format(trade.volume, trade.price))
        self._stop[trade.instrument] = (trade.price * self._percent, trade.volume)

    async def onSold(self, event: Event) -> None:
        trade: Trade = event.target  # type: ignore
        print('sold {:.2f} @ {:.2f}'.format(trade.volume, trade.price))
        del self._stop[trade.instrument]

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
        import matplotlib  # type: ignore
        import matplotlib.pyplot as plt  # type: ignore
        import numpy as np  # type: ignore
        import pandas as pd  # type: ignore

        # assemble portfolio
        instruments = []
        portfolio = []
        price_cols = []
        pnl_cols = []

        for position in self.positions():
            instrument = position.instrument
            instruments.append(instrument)

            #########
            # Price #
            #########
            price_col = instrument.name
            price_cols.append(price_col)
            price_history = pd.DataFrame(position.instrumentPriceHistory, columns=[price_col, 'when'])
            price_history.set_index('when', inplace=True)
            portfolio.append(price_history)

            #######
            # Pnl #
            #######
            unrealized_pnl_col = 'ur:{}'.format(instrument.name)
            pnl_cols.append(unrealized_pnl_col)
            unrealized_pnl_history = pd.DataFrame(position.unrealizedPnlHistory, columns=[unrealized_pnl_col, 'when'])
            unrealized_pnl_history.set_index('when', inplace=True)
            portfolio.append(unrealized_pnl_history)

            realized_pnl_col = 'r:{}'.format(instrument.name)
            pnl_cols.append(realized_pnl_col)
            realized_pnl_history = pd.DataFrame(position.pnlHistory, columns=[realized_pnl_col, 'when'])
            realized_pnl_history.set_index('when', inplace=True)
            portfolio.append(realized_pnl_history)

        # join along time axis
        df = pd.concat(portfolio, sort=True)
        df.sort_index(inplace=True)
        df.fillna(method='ffill', inplace=True)

        df_pnl = df[pnl_cols]
        df_price = df[price_cols]

        df_pnl.fillna(0.0, inplace=True)

        ################
        # calculations #
        ################
        # calculate total pnl
        df_pnl['alpha'] = sum(df_pnl[col] for col in pnl_cols)

        ############
        # Plotting #
        ############
        fig, axes = plt.subplots(3, 1, sharex=True, figsize=(14, 17))

        # Plot prices
        df_price[price_cols].plot(ax=axes[0], colormap='Greys', logy=True)
        axes[0].set_ylabel('Price')

        # Plot PNLs
        cm = matplotlib.cm.get_cmap("Paired")
        ls = np.linspace(0, 1, len(pnl_cols) // 2)
        colormap = []
        for i in ls:
            colormap.extend([matplotlib.colors.to_hex(cm(i)), matplotlib.colors.to_hex(cm(i + .05))])

        df_pnl[pnl_cols].plot(ax=axes[1], colors=colormap)
        axes[1].set_ylabel('Amt')

        # Plot up/down chart
        df2 = df_pnl[['alpha']]
        df2['pos'] = df2['alpha']
        df2['neg'] = df2['alpha']
        df2['pos'][df2['pos'] <= 0] = np.nan
        df2['neg'][df2['neg'] > 0] = np.nan
        df2.plot(ax=axes[2], y=['pos', 'neg'], kind='area', stacked=False, color=['green', 'red'], legend=False, linewidth=0, fontsize=5, rot=0)
        axes[2].set_ylabel('Alpha')
        axes[2].set_ylabel('Amt')

        plt.show()

        if input('IPython? (y/N)').strip().lower() == 'y':
            import IPython
            IPython.embed()
