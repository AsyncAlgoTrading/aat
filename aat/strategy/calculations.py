import os
import os.path
import types
from datetime import datetime
from typing import Set

import matplotlib.pyplot as plt  # type: ignore
import numpy as np  # type: ignore
import pandas as pd  # type: ignore


class CalculationsMixin(object):
    __perf_charts: Set[object] = set()  # TODO move
    __save_dir: str = ''  # TODO move

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

        self._df_investment = self.portfolio().getInvestment(self)
        self._df_investment.columns = [c.replace('i:', '') for c in self._df_investment.columns]

        if not self._df_size.empty:
            self._df_size.plot(kind='area', ax=ax, stacked=True, linewidth=0, **plot_kwargs)

        if ax:
            ax.set_ylabel('Positions')

    def plotPositionsAll(self, ax=None, **plot_kwargs):
        self._df_size_all = self.portfolio().getSizeAll()
        self._df_size_all.columns = [c.replace('s:', '') for c in self._df_size_all.columns]

        self._df_investment = self.portfolio().getInvestment(self)
        self._df_investment.columns = [c.replace('i:', '') for c in self._df_investment.columns]

        if not self._df_size_all.empty:
            self._df_size_all.plot(kind='area', ax=ax, stacked=True, linewidth=0, **plot_kwargs)

        if ax:
            ax.set_ylabel('Positions')

    def plotNotional(self, ax=None, **plot_kwargs):
        self._df_asset_price = self.portfolio().getAssetPrice(self)
        self._df_position_notional = self.portfolio().getSize(self)
        self._df_position_notional.columns = [c.replace('s:', '') for c in self._df_size.columns]

        for col in self._df_position_notional.columns:
            self._df_position_notional[col] = self._df_position_notional[col] * self._df_asset_price[col]

        if not self._df_position_notional.empty:
            self._df_position_notional.fillna(method='ffill', inplace=True)
            self._df_position_notional.plot(kind='area', ax=ax, stacked=True, linewidth=0, **plot_kwargs)

        if ax:
            ax.set_ylabel('Notional')

    def plotNotionalAll(self, ax=None, **plot_kwargs):
        self._df_asset_price = self.portfolio().getAssetPrice(self)
        self._df_position_notional_all = self.portfolio().getSizeAll()
        self._df_position_notional_all.columns = [c.replace('s:', '') for c in self._df_size_all.columns]

        for col in self._df_position_notional_all.columns:
            self._df_position_notional_all[col] = self._df_position_notional_all[col] * self._df_asset_price[col]

        if not self._df_position_notional_all.empty:
            self._df_position_notional_all.fillna(method='ffill', inplace=True)
            self._df_position_notional_all.plot(kind='area', ax=ax, stacked=True, linewidth=0, **plot_kwargs)

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

    def plotPnlAll(self, ax=None, **plot_kwargs):
        self._df_pnl_all = self.portfolio().getPnlAll()
        self._df_pnl_all.fillna(0.0, inplace=True)

        self._df_total_pnl_all = self._df_pnl_all[[c for c in self._df_pnl_all if 'pnl:' in c]]
        self._df_total_pnl_all.columns = [c.replace('pnl:', '') for c in self._df_total_pnl_all.columns]

        if not self._df_total_pnl_all.empty:
            self._df_total_pnl_all.plot(ax=ax)

        if ax:
            ax.set_ylabel('PNL')

    def plotUpDown(self, ax=None, **plot_kwargs):
        self._df_pnl = self.portfolio().getPnl(self)
        self._df_pnl.fillna(0.0, inplace=True)

        self._df_up_down = self._df_pnl[['alpha']]
        self._df_up_down['pos'] = self._df_up_down['alpha']
        self._df_up_down['neg'] = self._df_up_down['alpha']
        self._df_up_down['pos'][self._df_up_down['pos'] <= 0] = np.nan
        self._df_up_down['neg'][self._df_up_down['neg'] > 0] = np.nan

        if not self._df_up_down.empty:
            self._df_up_down.plot(ax=ax, y=['pos', 'neg'], kind='area', stacked=False, color=['green', 'red'], legend=False, linewidth=0, fontsize=5, rot=0, **plot_kwargs)

        if ax:
            ax.set_ylabel('Alpha')

    def plotUpDownAll(self, ax=None, **plot_kwargs):
        self._df_pnl_all = self.portfolio().getPnlAll()
        self._df_pnl_all.fillna(0.0, inplace=True)

        self._df_up_down_all = self._df_pnl_all[['alpha']]
        self._df_up_down_all['pos'] = self._df_up_down_all['alpha']
        self._df_up_down_all['neg'] = self._df_up_down_all['alpha']
        self._df_up_down_all['pos'][self._df_up_down_all['pos'] <= 0] = np.nan
        self._df_up_down_all['neg'][self._df_up_down_all['neg'] > 0] = np.nan

        if not self._df_up_down_all.empty:
            self._df_up_down_all.plot(ax=ax, y=['pos', 'neg'], kind='area', stacked=False, color=['green', 'red'], legend=False, linewidth=0, fontsize=5, rot=0, **plot_kwargs)

        if ax:
            ax.set_ylabel('Alpha')

    def plotReturnHistograms(self, ax, **plot_kwargs):
        self._df_notional = self.portfolio().getNotional(self)
        self._df_notional.columns = [c.replace('n:', '') for c in self._df_notional.columns]

        df_returns = []
        for col in self._df_notional.columns:
            # drop if exactly -100% (e.g. "sold")
            df_returns.append(self._df_notional[col].drop_duplicates().pct_change(1).dropna().shift(-1).fillna(0.0))

        if df_returns:
            self._df_returns = pd.concat(df_returns, axis=1, sort=True)
            self._df_returns.sort_index(inplace=True)
            self._df_returns = self._df_returns.groupby(self._df_returns.index).last()
            self._df_returns.drop_duplicates(inplace=True)
            self._df_returns.plot(kind='hist', ax=ax, sharex=True, stacked=True, bins=10, histtype='bar')

    def plotReturnHistogramsAll(self, ax, **plot_kwargs):
        self._df_notional_all = self.portfolio().getNotionalAll()
        self._df_notional_all.columns = [c.replace('n:', '') for c in self._df_notional_all.columns]

        df_returns = []
        for col in self._df_notional_all.columns:
            # drop if exactly -100% (e.g. "sold")
            df_returns.append(self._df_notional_all[col].drop_duplicates().pct_change(1).dropna().shift(-1).fillna(0.0))

        if df_returns:
            self._df_returns_all = pd.concat(df_returns, axis=1, sort=True)
            self._df_returns_all.sort_index(inplace=True)
            self._df_returns_all = self._df_returns_all.groupby(self._df_returns_all.index).last()
            self._df_returns_all.drop_duplicates(inplace=True)

            self._df_returns_all.plot(kind='hist', ax=ax, sharex=True, stacked=True, bins=10, histtype='bar')

    def plotStdDev(self, ax, **plot_kwargs):
        self._df_notional = self.portfolio().getNotional(self)
        self._df_notional.columns = [c.replace('n:', '') for c in self._df_notional.columns]

        if not self._df_notional.empty:
            self._total_returns = self._df_notional.sum(axis=1).pct_change(1).fillna(0.0)
            self._total_returns_stddev = self._total_returns.rolling(10)
            self._total_returns_stddev.std().plot(ax=ax)
            ax.axhline(self._total_returns.std())
            ax.set_ylabel('Std.')

    def plotStdDevAll(self, ax, **plot_kwargs):
        self._df_notional_all = self.portfolio().getNotionalAll()
        self._df_notional_all.columns = [c.replace('n:', '') for c in self._df_notional_all.columns]

        if not self._df_notional_all.empty:
            self._total_returns_all = self._df_notional_all.sum(axis=1).pct_change(1).fillna(0.0)
            self._total_returns_stddev_all = self._total_returns_all.rolling(10)
            self._total_returns_stddev_all.std().plot(ax=ax)
            ax.axhline(self._total_returns_all.std())
            ax.set_ylabel('Std.')

    def plotSharpe(self, ax, **plot_kwargs):
        self._df_notional = self.portfolio().getNotional(self)
        self._df_notional.columns = [c.replace('n:', '') for c in self._df_notional.columns]

        if not self._df_notional.empty:
            self._total_returns_sharpe = self._df_notional.sum(axis=1).pct_change(1).fillna(0.0)

            sharpe = self._total_returns_sharpe.values.mean() / self._total_returns_sharpe.values.std() * np.sqrt(252)
            self._total_returns_sharpe['sharpe'] = self._total_returns_sharpe.rolling(20).mean() / self._total_returns_sharpe.rolling(10).std() * np.sqrt(252)
            self._total_returns_sharpe['sharpe'].plot(ax=ax)
            ax.axhline(sharpe)
            ax.set_ylabel('Sharpe')

    def plotSharpeAll(self, ax, **plot_kwargs):
        self._df_notional_all = self.portfolio().getNotionalAll()
        self._df_notional_all.columns = [c.replace('n:', '') for c in self._df_notional_all.columns]

        if not self._df_notional_all.empty:
            self._total_returns_sharpe_all = self._df_notional_all.sum(axis=1).pct_change(1).fillna(0.0)

            sharpe = self._total_returns_sharpe_all.values.mean() / self._total_returns_sharpe_all.values.std() * np.sqrt(252)
            self._total_returns_sharpe_all['sharpe'] = self._total_returns_sharpe_all.rolling(20).mean() / self._total_returns_sharpe_all.rolling(10).std() * np.sqrt(252)
            self._total_returns_sharpe_all['sharpe'].plot(ax=ax)
            ax.axhline(sharpe)
            ax.set_ylabel('Sharpe')

    def performanceByStrategy(self, save=False, save_data=False):
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

        if save:
            plt.savefig('{}/{}.pdf'.format(self._save_dir, self.name()))

        if save_data:
            self._writeoutPerf(self.name())

    def performanceByAsset(self, save=False, save_data=False):
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
        self.plotPositionsAll(ax=axes[1])

        # Plot Notionals
        self.plotNotionalAll(ax=axes[2])

        # Plot PNLs
        self.plotPnlAll(ax=axes[3])

        # Plot up/down chart
        self.plotUpDownAll(ax=axes[4])

        # rolling stddev
        self.plotStdDevAll(ax=axes[5])
        self.plotSharpeAll(ax=axes[6])

        # Plot returns
        self.plotReturnHistogramsAll(ax=axes[7])

        if save:
            plt.savefig('{}/all.pdf'.format(self._save_dir))

        if save_data:
            self._writeoutPerf('all')

    def performanceCharts(self, strategy=None, render=True, save=False, save_data=False):
        '''Render performance charts to analyze strategy results

        Args:
            strategy (str): show plot for the strategy with this name (useful for offline inspection)
            render (bool): render charts with matplotlib, default=True
            save (bool): save charts as pdf to disk, default=False
            save_data (bool): save data to disk, default=False
        '''

        if save or save_data:
            if not CalculationsMixin.__save_dir:
                CalculationsMixin.__save_dir = '_aat_{}_{}'.format(self.tradingType(), datetime.now().isoformat())

            self._save_dir = CalculationsMixin.__save_dir
            os.makedirs(self._save_dir, exist_ok=True)

        if not CalculationsMixin.__perf_charts:
            CalculationsMixin.__total_count = self.__class__._ID_GENERATOR()

            if CalculationsMixin.__total_count > 1:
                # Only run once
                self.performanceByAsset(save=save, save_data=save_data)

        CalculationsMixin.__perf_charts.add(self)

        if strategy and self.name() != strategy:
            pass
        else:
            self.performanceByStrategy(save=save, save_data=save_data)

        if len(CalculationsMixin.__perf_charts) == CalculationsMixin.__total_count:
            if CalculationsMixin.__total_count < 5 and render:
                # Show plot
                plt.show()
            elif render:
                print('Too many strategies to render, try saving to pdf instead')

    def _writeoutPerf(self, filename):
        if filename == 'all':
            self._df_price.to_csv('{}/{}_df_price.csv'.format(self._save_dir, filename))
            self._df_pnl_all.to_csv('{}/{}_df_pnl.csv'.format(self._save_dir, filename))
            self._df_notional_all.to_csv('{}/{}_df_notional.csv'.format(self._save_dir, filename))
            self._df_size_all.to_csv('{}/{}_df_size.csv'.format(self._save_dir, filename))
            self._df_total_pnl_all.to_csv('{}/{}_df_total_pnl.csv'.format(self._save_dir, filename))
            self._df_up_down_all.to_csv('{}/{}_df_up_down.csv'.format(self._save_dir, filename))
            self._df_returns_all.to_csv('{}/{}_df_returns.csv'.format(self._save_dir, filename))
            self._total_returns_all.to_csv('{}/{}_total_returns.csv'.format(self._save_dir, filename))

            self._df_price.to_csv('{}/{}_df_price.csv'.format(self._save_dir, filename))
            self._df_pnl_all.to_csv('{}/{}_df_pnl.csv'.format(self._save_dir, filename))
            self._df_notional_all.to_csv('{}/{}_df_notional.csv'.format(self._save_dir, filename))
            self._df_size_all.to_csv('{}/{}_df_size.csv'.format(self._save_dir, filename))
            self._df_total_pnl_all.to_csv('{}/{}_df_total_pnl.csv'.format(self._save_dir, filename))
            self._df_up_down_all.to_csv('{}/{}_df_up_down.csv'.format(self._save_dir, filename))
            self._df_returns_all.to_csv('{}/{}_df_returns.csv'.format(self._save_dir, filename))
            self._total_returns_all.to_csv('{}/{}_total_returns.csv'.format(self._save_dir, filename))

        else:
            self._df_price.to_csv('{}/{}_df_price.csv'.format(self._save_dir, filename))
            self._df_pnl.to_csv('{}/{}_df_pnl.csv'.format(self._save_dir, filename))
            self._df_notional.to_csv('{}/{}_df_notional.csv'.format(self._save_dir, filename))
            self._df_investment.to_csv('{}/{}_df_investment.csv'.format(self._save_dir, filename))
            self._df_size.to_csv('{}/{}_df_size.csv'.format(self._save_dir, filename))
            self._df_position_notional.to_csv('{}/{}_df_position_notional.csv'.format(self._save_dir, filename))
            self._df_total_pnl.to_csv('{}/{}_df_total_pnl.csv'.format(self._save_dir, filename))
            self._df_up_down.to_csv('{}/{}_df_up_down.csv'.format(self._save_dir, filename))
            self._df_returns.to_csv('{}/{}_df_returns.csv'.format(self._save_dir, filename))
            self._total_returns.to_csv('{}/{}_total_returns.csv'.format(self._save_dir, filename))

            self._df_price.to_csv('{}/{}_df_price.csv'.format(self._save_dir, filename))
            self._df_pnl.to_csv('{}/{}_df_pnl.csv'.format(self._save_dir, filename))
            self._df_notional.to_csv('{}/{}_df_notional.csv'.format(self._save_dir, filename))
            self._df_investment.to_csv('{}/{}_df_investment.csv'.format(self._save_dir, filename))
            self._df_size.to_csv('{}/{}_df_size.csv'.format(self._save_dir, filename))
            self._df_position_notional.to_csv('{}/{}_df_position_notional.csv'.format(self._save_dir, filename))
            self._df_total_pnl.to_csv('{}/{}_df_total_pnl.csv'.format(self._save_dir, filename))
            self._df_up_down.to_csv('{}/{}_df_up_down.csv'.format(self._save_dir, filename))
            self._df_returns.to_csv('{}/{}_df_returns.csv'.format(self._save_dir, filename))
            self._total_returns.to_csv('{}/{}_total_returns.csv'.format(self._save_dir, filename))

        self.portfolio().save('{}/{}.portfolio'.format(self._save_dir, filename))

    def _portfolioRestore(self):
        self.portfolio().restore()

    def ipython(self):
        import IPython  # type: ignore
        IPython.embed()


def main():
    import argparse
    from aat.common import id_generator
    from aat.engine.dispatch import Portfolio

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--folder',
        help='Folder where backtest calculations are stored',
        required=True)

    parser.add_argument(
        '--strategy',
        help='Plot results for this strategy instance',
        required=True)

    parser.add_argument(
        '--render',
        help='Plot results?',
        default=True)

    args = parser.parse_args()

    portfolio = Portfolio()
    portfolio.restore('{}/{}.portfolio'.format(args.folder.rstrip('/'), args.strategy))

    calculator = CalculationsMixin()

    # Fill in mixin
    # TODO ugly
    CalculationsMixin._ID_GENERATOR = id_generator()
    CalculationsMixin._ID_GENERATOR()  # count 1
    calculator.portfolio = types.MethodType(lambda self, p=portfolio: p, calculator)
    calculator.name = types.MethodType(lambda self, name=args.strategy: name, calculator)

    calculator.performanceCharts(args.strategy, args.render != "False", False, False)


if __name__ == '__main__':
    main()
