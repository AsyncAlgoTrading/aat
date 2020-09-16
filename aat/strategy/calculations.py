from typing import Set

import matplotlib.pyplot as plt  # type: ignore
import numpy as np  # type: ignore
import pandas as pd  # type: ignore


class CalculationsMixin(object):
    __perf_charts: Set[object] = set()  # TODO move

    def collectStats(self):
        # assemble portfolio
        self._df_pnl = self.portfolio().getPnl(self)
        self._df_pnl.fillna(0.0, inplace=True)

        self._df_asset_price = self.portfolio().getAssetPrice(self)

        self._df_total_pnl = self._df_pnl[[c for c in self._df_pnl if 'pnl:' in c]]
        self._df_total_pnl.columns = [c.replace('pnl:', '') for c in self._df_total_pnl.columns]

        self._df_size = self.portfolio().getSize(self)
        self._df_size.columns = [c.replace('s:', '') for c in self._df_size.columns]

        self._df_notional = self.portfolio().getNotional(self)
        self._df_notional.columns = [c.replace('n:', '') for c in self._df_notional.columns]

        self._df_investment = self.portfolio().getInvestment(self)
        self._df_investment.columns = [c.replace('i:', '') for c in self._df_investment.columns]

    def plotPrice(self, ax=None, **plot_kwargs):
        self._df_price = self.portfolio().getPrice()

        if not self._df_price.empty:
            self._df_price.plot(ax=ax, **plot_kwargs)

        if ax:
            ax.set_ylabel('Price')

    def plotAssetPrice(self, ax=None, **plot_kwargs):
        self._df_asset_price = self.portfolio().getAssetPrice(self)

        if not self._df_asset_price.empty:
            self._df_asset_price.plot(ax=ax, **plot_kwargs)

        if ax:
            ax.set_ylabel('Price')

    def plotPositions(self, ax=None, **plot_kwargs):
        self._df_size = self.portfolio().getSize(self)
        self._df_size.columns = [c.replace('s:', '') for c in self._df_size.columns]

        if not self._df_size.empty:
            self._df_size.plot(kind='area', ax=ax, stacked=True, linewidth=0, **plot_kwargs)

        if ax:
            ax.set_ylabel('Positions')

    def plotNotional(self, ax=None, **plot_kwargs):
        df_position_notional = self.portfolio().getSize(self)
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
        self._df_pnl = self.portfolio().getPnl(self)
        self._df_pnl.fillna(0.0, inplace=True)

        self._df_total_pnl = self._df_pnl[[c for c in self._df_pnl if 'pnl:' in c]]
        self._df_total_pnl.columns = [c.replace('pnl:', '') for c in self._df_total_pnl.columns]

        if not self._df_total_pnl.empty:
            self._df_total_pnl.plot(ax=ax)

        if ax:
            ax.set_ylabel('PNL')

    def plotUpDown(self, ax=None, **plot_kwargs):
        self._df_pnl = self.portfolio().getPnl(self)
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

    def plotReturnHistograms(self, ax, **plot_kwargs):
        self._df_notional = self.portfolio().getNotional(self)
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

        df_returns.plot(kind='hist', ax=ax, sharex=True, stacked=True, bins=10, histtype='bar')

    def plotStdDev(self, ax, **plot_kwargs):
        self._df_notional = self.portfolio().getNotional(self)
        self._df_notional.columns = [c.replace('n:', '') for c in self._df_notional.columns]

        if not self._df_notional.empty:
            total_returns = self._df_notional.sum(axis=1).pct_change(1).fillna(0.0)
            total_returns_rolling = total_returns.rolling(10)
            total_returns_rolling.std().plot(ax=ax)
            ax.axhline(total_returns.std())
            ax.set_ylabel('Std.')

    def plotSharpe(self, ax, **plot_kwargs):
        self._df_notional = self.portfolio().getNotional(self)
        self._df_notional.columns = [c.replace('n:', '') for c in self._df_notional.columns]

        if not self._df_notional.empty:
            total_returns = self._df_notional.sum(axis=1).pct_change(1).fillna(0.0)

            sharpe = total_returns.values.mean() / total_returns.values.std() * np.sqrt(252)
            total_returns['sharpe'] = total_returns.rolling(20).mean() / total_returns.rolling(10).std() * np.sqrt(252)
            total_returns['sharpe'].plot(ax=ax)
            ax.axhline(sharpe)
            ax.set_ylabel('Sharpe')

    def performanceByStrategy(self):
        fig, axes = plt.subplots(8, 1,
                                 figsize=(7, 10),
                                 gridspec_kw={'height_ratios': [3, 2, 2, 3, 2, 1, 1, 3]})
        # join all but last on x axis
        for ax in axes[:-1]:
            axes[0].get_shared_x_axes().join(axes[0], ax)

        plt.rc('legend', fontsize=4)  # using a size in points
        fig.suptitle("Summary ({})".format(self.name()))

        # Plot prices
        self.plotPrice(ax=axes[0])

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
        self.plotReturnHistograms(ax=axes[7])

    def performanceByAsset(self):
        fig, axes = plt.subplots(8, 1,
                                 figsize=(7, 10),
                                 gridspec_kw={'height_ratios': [3, 2, 2, 3, 2, 1, 1, 3]})
        # join all but last on x axis
        for ax in axes[:-1]:
            axes[0].get_shared_x_axes().join(axes[0], ax)

        plt.rc('legend', fontsize=4)  # using a size in points
        fig.suptitle("Summary (by asset)")

        # Plot prices
        self.plotPrice(ax=axes[0])

        # Plot Positions
        # self.plotPositions(ax=axes[1])

        # Plot Notionals
        # self.plotNotional(ax=axes[2])

        # Plot PNLs
        # self.plotPnl(ax=axes[3])

        # Plot up/down chart
        # self.plotUpDown(ax=axes[4])

        # rolling stddev
        # self.plotStdDev(ax=axes[5])
        # self.plotSharpe(ax=axes[6])

        # Plot returns
        # self.plotReturnHistograms(ax=axes[7])

    def performanceCharts(self):
        if self not in CalculationsMixin.__perf_charts:
            self.collectStats()

        if not CalculationsMixin.__perf_charts:
            # Only run once
            self.performanceByAsset()

            CalculationsMixin.__total_count = self.__class__._ID_GENERATOR()

        CalculationsMixin.__perf_charts.add(self)
        self.performanceByStrategy()

        if len(CalculationsMixin.__perf_charts) == CalculationsMixin.__total_count:
            # Show plot
            plt.show()

    def ipython(self):
        import IPython  # type: ignore
        IPython.embed()
