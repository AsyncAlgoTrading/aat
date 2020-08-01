import math
from aat import Strategy, Event, Order, Trade, Side


class SellPlusPercentStrategy(Strategy):
    def __init__(self, percent=10, *args, **kwargs) -> None:
        super(SellPlusPercentStrategy, self).__init__(*args, **kwargs)

        self._up_percent = 1.0 + float(percent) / 100
        self._down_percent = 1.0 - float(percent) / 100
        self._stop = {}

    async def onTrade(self, event: Event) -> None:
        '''Called whenever a `Trade` event is received'''
        trade: Trade = event.target  # type: ignore

        # no current orders, no past trades
        if not self.orders(trade.instrument) and not self.trades(trade.instrument):
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
                    trade.instrument in self._stop and \
                    (trade.price >= self._stop[trade.instrument][0] or
                     trade.price <= self._stop[trade.instrument][1]):
                req = Order(side=Side.SELL,
                            price=trade.price,
                            volume=self._stop[trade.instrument][2],
                            instrument=trade.instrument,
                            order_type=Order.Types.MARKET,
                            exchange=trade.exchange)

                print('requesting sell : {}'.format(req))
                await self.newOrder(req)

    async def onBought(self, event: Event) -> None:
        trade: Trade = event.target  # type: ignore
        print('bought {:.2f} @ {:.2f}'.format(trade.volume, trade.price))
        self._stop[trade.instrument] = (trade.price * self._up_percent,
                                        trade.price * self._down_percent,
                                        trade.volume)

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
        # import matplotlib  # type: ignore
        import matplotlib.pyplot as plt  # type: ignore
        import numpy as np  # type: ignore
        import pandas as pd  # type: ignore

        # assemble portfolio
        instruments = []
        portfolio = []
        price_cols = []
        pnl_cols = []
        total_pnl_cols = []
        size_cols = []
        notional_cols = []
        investment_cols = []

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
            total_pnl_col = 'pnl:{}'.format(instrument.name)
            unrealized_pnl_col = 'ur:{}'.format(instrument.name)
            pnl_cols.append(unrealized_pnl_col)
            unrealized_pnl_history = pd.DataFrame(position.unrealizedPnlHistory, columns=[unrealized_pnl_col, 'when'])
            unrealized_pnl_history.set_index('when', inplace=True)

            realized_pnl_col = 'r:{}'.format(instrument.name)
            pnl_cols.append(realized_pnl_col)
            realized_pnl_history = pd.DataFrame(position.pnlHistory, columns=[realized_pnl_col, 'when'])
            realized_pnl_history.set_index('when', inplace=True)

            unrealized_pnl_history[realized_pnl_col] = realized_pnl_history[realized_pnl_col]
            unrealized_pnl_history[total_pnl_col] = unrealized_pnl_history.sum(axis=1)
            total_pnl_cols.append(total_pnl_col)
            portfolio.append(unrealized_pnl_history)

            #################
            # Position Size #
            #################
            size_col = 's:{}'.format(instrument.name)
            size_cols.append(size_col)
            size_history = pd.DataFrame(position.sizeHistory, columns=[size_col, 'when'])
            size_history.set_index('when', inplace=True)
            portfolio.append(size_history)

            notional_col = 'n:{}'.format(instrument.name)
            notional_cols.append(notional_col)
            notional_history = pd.DataFrame(position.notionalHistory, columns=[notional_col, 'when'])
            notional_history.set_index('when', inplace=True)
            portfolio.append(notional_history)

            investment_col = 'i:{}'.format(instrument.name)
            investment_cols.append(investment_col)
            investment_history = pd.DataFrame(position.investmentHistory, columns=[investment_col, 'when'])
            investment_history.set_index('when', inplace=True)
            portfolio.append(investment_history)

        # join along time axis
        df = pd.concat(portfolio, sort=True)
        df.sort_index(inplace=True)
        df = df.groupby(df.index).last()
        df.drop_duplicates(inplace=True)
        df.fillna(method='ffill', inplace=True)

        df_pnl = df[pnl_cols]
        df_pnl.fillna(0.0, inplace=True)

        # df_total_pnl = df[total_pnl_cols]
        df_price = df[price_cols]

        df_size = df[size_cols]
        df_size.columns = [c.replace('s:', '') for c in df_size.columns]

        df_notional = df[notional_cols]
        df_notional.columns = [c.replace('n:', '') for c in df_notional.columns]

        df_investment = df[investment_cols]
        df_investment.columns = [c.replace('i:', '') for c in df_investment.columns]

        ################
        # calculations #
        ################
        # calculate total pnl
        df_pnl['alpha'] = df_pnl.sum(axis=1)

        ############
        # Plotting #
        ############
        fig, axes = plt.subplots(5, 1,
                                 sharex=True,
                                 figsize=(7, 7),
                                 gridspec_kw={'height_ratios': [2, 1, 3, 1, 1]})
        plt.rc('legend', fontsize=4)  # using a size in points

        # Plot prices
        df_price[price_cols].plot(ax=axes[0])
        axes[0].set_ylabel('Price')

        # Plot Positions
        df_size.plot(kind='area', ax=axes[1], stacked=True, linewidth=0)
        axes[1].set_ylabel('Position Size')

        df_position_notional = df_size.copy()
        for col in df_position_notional.columns:
            df_position_notional[col] = df_position_notional[col] * df_price[col]

        df_position_notional.plot(kind='area', ax=axes[2], stacked=True, linewidth=0)
        axes[2].set_ylabel('Position Size')

        # Plot PNLs
        # cm = matplotlib.cm.get_cmap("Paired")
        # ls = np.linspace(0, 1, len(pnl_cols) // 2)
        # colors = []
        # for i in ls:
        #     colors.extend([matplotlib.colors.to_hex(cm(i)), matplotlib.colors.to_hex(cm(i + .05))])

        df[total_pnl_cols].plot(ax=axes[3])
        axes[3].set_ylabel('PNL')

        # Plot up/down chart
        df2 = df_pnl[['alpha']]
        df2['pos'] = df2['alpha']
        df2['neg'] = df2['alpha']
        df2['pos'][df2['pos'] <= 0] = np.nan
        df2['neg'][df2['neg'] > 0] = np.nan
        df2.plot(ax=axes[4], y=['pos', 'neg'], kind='area', stacked=False, color=['green', 'red'], legend=False, linewidth=0, fontsize=5, rot=0)
        axes[4].set_ylabel('Alpha')

        # Plot returns
        df_returns = []
        for col in df_notional.columns:
            df_notional[col].drop_duplicates().pct_change(1).fillna(0.0)
            # drop if exactly -100% (e.g. "sold")
            df_returns.append(df_notional[col].drop_duplicates().pct_change(1).fillna(0.0))

        df_returns = pd.concat(df_returns, axis=1, sort=True)
        df_returns.sort_index(inplace=True)
        df_returns = df_returns.groupby(df_returns.index).last()
        df_returns.drop_duplicates(inplace=True)

        fig2 = plt.figure(figsize=(7, 7))
        grid = plt.GridSpec(2, len(df_returns.columns), figure=fig2, wspace=0.4, hspace=0.3)
        axes2 = []
        for _ in range(len(df_returns.columns)):
            axes2.append(plt.subplot(grid[0, _]))

        for i, col in enumerate(df_returns.columns):
            df_returns.hist(column=col, ax=axes2[i], grid=False)

        plt.show()

        # if input('IPython? (y/N)').strip().lower() == 'y':
        #     import IPython
        #     IPython.embed()
