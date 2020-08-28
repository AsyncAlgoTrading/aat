import matplotlib.pyplot as plt  # type: ignore
import numpy as np  # type: ignore
import pandas as pd  # type: ignore


class CalculationsMixin(object):
    __perf_charts = False  # TODO move

    def _constructDf(self, dfs, drop_duplicates=True):
        # join along time axis
        if dfs:
            df = pd.concat(dfs, sort=True)
            df.sort_index(inplace=True)
            df = df.groupby(df.index).last()

            if drop_duplicates:
                df.drop_duplicates(inplace=True)

            df.fillna(method='ffill', inplace=True)
        else:
            df = pd.DataFrame()
        return df

    def _getInstruments(self):
        instruments = []
        for position in self.positions():
            instrument = position.instrument
            instruments.append(instrument)
        return instruments

    def _getPrice(self):
        portfolio = []
        price_cols = []
        for instrument, price_history in self.priceHistory().items():
            #########
            # Price #
            #########
            price_col = instrument.name
            price_cols.append(price_col)
            price_history.set_index('when', inplace=True)
            portfolio.append(price_history)
        return self._constructDf(portfolio)

    def _getAssetPrice(self):
        portfolio = []
        price_cols = []
        for position in self.positions():
            instrument = position.instrument

            #########
            # Price #
            #########
            price_col = instrument.name
            price_cols.append(price_col)
            price_history = pd.DataFrame(position.instrumentPriceHistory, columns=[price_col, 'when'])
            price_history.set_index('when', inplace=True)
            portfolio.append(price_history)
        return self._constructDf(portfolio)

    def _getPnl(self):
        portfolio = []
        pnl_cols = []
        total_pnl_cols = []
        for position in self.positions():
            instrument = position.instrument

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

        df_pnl = self._constructDf(portfolio, drop_duplicates=False)  # dont drop duplicates

        ################
        # calculations #
        ################
        # calculate total pnl
        df_pnl['alpha'] = df_pnl[[c for c in df_pnl.columns if c.startswith('pnl:')]].sum(axis=1)
        return df_pnl

    def _getSize(self):
        portfolio = []
        size_cols = []
        for position in self.positions():
            instrument = position.instrument

            #################
            # Position Size #
            #################
            size_col = 's:{}'.format(instrument.name)
            size_cols.append(size_col)
            size_history = pd.DataFrame(position.sizeHistory, columns=[size_col, 'when'])
            size_history.set_index('when', inplace=True)
            portfolio.append(size_history)

            price_col = instrument.name
            price_history = pd.DataFrame(position.instrumentPriceHistory, columns=[price_col, 'when'])
            price_history.set_index('when', inplace=True)
            portfolio.append(price_history)

        return self._constructDf(portfolio)[size_cols]

    def _getNotional(self):
        portfolio = []
        notional_cols = []
        for position in self.positions():
            instrument = position.instrument

            #################
            # Position Size #
            #################
            notional_col = 'n:{}'.format(instrument.name)
            notional_cols.append(notional_col)
            notional_history = pd.DataFrame(position.notionalHistory, columns=[notional_col, 'when'])
            notional_history.set_index('when', inplace=True)
            portfolio.append(notional_history)

            price_col = instrument.name
            price_history = pd.DataFrame(position.instrumentPriceHistory, columns=[price_col, 'when'])
            price_history.set_index('when', inplace=True)
            portfolio.append(price_history)

        return self._constructDf(portfolio)[notional_cols]

    def _getInvestment(self):
        portfolio = []
        investment_cols = []
        for position in self.positions():
            instrument = position.instrument

            #################
            # Position Size #
            #################
            investment_col = 'i:{}'.format(instrument.name)
            investment_cols.append(investment_col)
            investment_history = pd.DataFrame(position.investmentHistory, columns=[investment_col, 'when'])
            investment_history.set_index('when', inplace=True)
            portfolio.append(investment_history)

            price_col = instrument.name
            price_history = pd.DataFrame(position.instrumentPriceHistory, columns=[price_col, 'when'])
            price_history.set_index('when', inplace=True)
            portfolio.append(price_history)

        return self._constructDf(portfolio)[investment_cols]

    def collectStats(self):
        # assemble portfolio
        self._df_pnl = self._getPnl()
        self._df_pnl.fillna(0.0, inplace=True)

        self._df_asset_price = self._getAssetPrice()

        self._df_total_pnl = self._df_pnl[[c for c in self._df_pnl if 'pnl:' in c]]
        self._df_total_pnl.columns = [c.replace('pnl:', '') for c in self._df_total_pnl.columns]

        self._df_size = self._getSize()
        self._df_size.columns = [c.replace('s:', '') for c in self._df_size.columns]

        self._df_notional = self._getNotional()
        self._df_notional.columns = [c.replace('n:', '') for c in self._df_notional.columns]

        self._df_investment = self._getInvestment()
        self._df_investment.columns = [c.replace('i:', '') for c in self._df_investment.columns]

    def plotPrice(self, ax=None, **plot_kwargs):
        self._df_price = self._getPrice()

        if not self._df_price.empty:
            self._df_price.plot(ax=ax, **plot_kwargs)

        if ax:
            ax.set_ylabel('Price')

    def plotAssetPrice(self, ax=None, **plot_kwargs):
        self._df_asset_price = self._getAssetPrice()

        if not self._df_asset_price.empty:
            self._df_asset_price.plot(ax=ax, **plot_kwargs)

        if ax:
            ax.set_ylabel('Price')

    def plotPositions(self, ax=None, **plot_kwargs):
        self._df_size = self._getSize()
        self._df_size.columns = [c.replace('s:', '') for c in self._df_size.columns]

        if not self._df_size.empty:
            self._df_size.plot(kind='area', ax=ax, stacked=True, linewidth=0, **plot_kwargs)

        if ax:
            ax.set_ylabel('Positions')

    def plotNotional(self, ax=None, **plot_kwargs):
        df_position_notional = self._getSize()
        df_position_notional.columns = [c.replace('s:', '') for c in self._df_size.columns]

        for col in df_position_notional.columns:
            df_position_notional[col] = df_position_notional[col] * self._df_asset_price[col]

        if not df_position_notional.empty:
            df_position_notional.fillna(method='ffill', inplace=True)
            df_position_notional.plot(kind='area', ax=ax, stacked=True, linewidth=0, **plot_kwargs)

        if ax:
            ax.set_ylabel('Notional')

    def plotPnl(self, ax=None, **plot_kwargs):
        # cm = matplotlib.cm.get_cmap("Paired")
        # ls = np.linspace(0, 1, len(pnl_cols) // 2)
        # colors = []
        # for i in ls:
        #     colors.extend([matplotlib.colors.to_hex(cm(i)), matplotlib.colors.to_hex(cm(i + .05))])
        self._df_pnl = self._getPnl()
        self._df_pnl.fillna(0.0, inplace=True)

        self._df_total_pnl = self._df_pnl[[c for c in self._df_pnl if 'pnl:' in c]]
        self._df_total_pnl.columns = [c.replace('pnl:', '') for c in self._df_total_pnl.columns]

        if not self._df_total_pnl.empty:
            self._df_total_pnl.plot(ax=ax)

        if ax:
            ax.set_ylabel('PNL')

    def plotUpDown(self, ax=None, **plot_kwargs):
        self._df_pnl = self._getPnl()
        self._df_pnl.fillna(0.0, inplace=True)

        df2 = self._df_pnl[['alpha']]
        df2['pos'] = df2['alpha']
        df2['neg'] = df2['alpha']
        df2['pos'][df2['pos'] <= 0] = np.nan
        df2['neg'][df2['neg'] > 0] = np.nan

        if not df2.empty:
            df2.plot(ax=ax, y=['pos', 'neg'], kind='area', stacked=False, color=['green', 'red'], legend=False, linewidth=0, fontsize=5, rot=0, **plot_kwargs)

        if ax:
            ax.set_ylabel('Alpha')

    def plotReturnHistograms(self, **plot_kwargs):
        self._df_notional = self._getNotional()
        self._df_notional.columns = [c.replace('n:', '') for c in self._df_notional.columns]

        df_returns = []
        for col in self._df_notional.columns:
            self._df_notional[col].drop_duplicates().pct_change(1).fillna(0.0)
            # drop if exactly -100% (e.g. "sold")
            df_returns.append(self._df_notional[col].drop_duplicates().pct_change(1).fillna(0.0))

        if df_returns:
            df_returns = pd.concat(df_returns, axis=1, sort=True)
            df_returns.sort_index(inplace=True)
            df_returns = df_returns.groupby(df_returns.index).last()
            df_returns.drop_duplicates(inplace=True)

            fig2 = plt.figure(figsize=(9, 5))
            grid = plt.GridSpec(2, len(df_returns.columns), figure=fig2, wspace=0.4, hspace=0.3)
            axes2 = []
            for _ in range(len(df_returns.columns)):
                axes2.append(plt.subplot(grid[0, _]))

            for i, col in enumerate(df_returns.columns):
                df_returns.hist(column=col, ax=axes2[i], grid=False)

    def plotStdDev(self, ax, **plot_kwargs):
        self._df_notional = self._getNotional()
        self._df_notional.columns = [c.replace('n:', '') for c in self._df_notional.columns]

        if not self._df_notional.empty:
            total_returns = self._df_notional.sum(axis=1).pct_change(1).fillna(0.0)
            total_returns_rolling = total_returns.rolling(10)
            total_returns_rolling.std().plot(ax=ax)
            ax.axhline(total_returns.std())
            ax.set_ylabel('Std.')

    def plotSharpe(self, ax, **plot_kwargs):
        self._df_notional = self._getNotional()
        self._df_notional.columns = [c.replace('n:', '') for c in self._df_notional.columns]

        if not self._df_notional.empty:
            total_returns = self._df_notional.sum(axis=1).pct_change(1).fillna(0.0)

            sharpe = total_returns.values.mean() / total_returns.values.std() * np.sqrt(252)
            total_returns['sharpe'] = total_returns.rolling(20).mean() / total_returns.rolling(10).std() * np.sqrt(252)
            total_returns['sharpe'].plot(ax=ax)
            ax.axhline(sharpe)
            ax.set_ylabel('Sharpe')

    def performanceCharts(self):
        if not CalculationsMixin.__perf_charts:
            self.collectStats()

            ############
            # Plotting #
            ############
            fig, axes = plt.subplots(7, 1,
                                     sharex=True,
                                     figsize=(7, 7),
                                     gridspec_kw={'height_ratios': [2, 1, 3, 1, 1, 1, 1]})
            plt.rc('legend', fontsize=4)  # using a size in points

            # Plot prices
            self.plotPrice(ax=axes[0])
            # self.plotAssetPrice(ax=axes[1])

            # Plot Positions
            self.plotPositions(ax=axes[1])

            # Plot Notionals
            self.plotNotional(ax=axes[2])

            # Plot PNLs
            self.plotPnl(ax=axes[3])

            # Plot up/down chart
            self.plotUpDown(ax=axes[4])

            # rolling stddev
            self.plotStdDev(ax=axes[5])
            self.plotSharpe(ax=axes[6])

            # Plot returns
            self.plotReturnHistograms()

            # Show plot
            plt.show()

            # Only show once
            CalculationsMixin.__perf_charts = True

    def ipython(self):
        import IPython  # type: ignore
        IPython.embed()
