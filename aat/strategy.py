from abc import ABCMeta, abstractmethod
from .callback import Callback
from .enums import Side
from .structs import TradeRequest, TradeResponse


class Strategy(metaclass=ABCMeta):
    '''Strategy interface'''

    def __init__(self, query=None, exchanges=None, *args, **kwargs) -> None:
        self.query = query
        self.exchanges = exchanges

    def setEngine(self, engine) -> None:
        self._te = engine

    @abstractmethod
    def request(self, req: TradeRequest):
        '''request'''


class TradingStrategy(Strategy, Callback):
    def request(self, req: TradeRequest) -> None:
        '''attempt to buy/sell'''
        return self._te.request(req, self)

    def cancel(self, resp: TradeResponse) -> None:
        '''cancel order'''
        return self._te.cancel(resp, self)

    def cancelAll(self):
        '''cancel all orders'''
        return self._te.cancelAll(self)

    def slippage(self, data: TradeResponse) -> TradeResponse:
        '''slippage model. default is pass through'''
        return data

    def transactionCost(self, data: TradeResponse) -> TradeResponse:
        '''txns cost model. default is pass through'''
        return data

    def to_dict(self, *args):
        return {'name': self.__class__.__name__}

    def onAnalyze(self, engine):
        '''onAnalyze'''
        pass
        if not engine:
            return
        import pandas
        import numpy as np
        import matplotlib
        import matplotlib.pyplot as plt
        import seaborn as sns
        matplotlib.rc('font', **{'size': 5})

        # extract data from trading engine
        positions_value = engine.query.positions_value
        portfolio_value = engine.query.portfolio_value

        requests = engine.query.query_tradereqs()
        responses = engine.query.query_traderesps()
        trades = pandas.DataFrame([{'time': x.time, 'price': x.price} for x in engine.query.query_trades(instrument=requests[0].instrument, page=None)])
        trades.set_index(['time'], inplace=True)

        # format into pandas
        pd = pandas.DataFrame(positions_value, columns=['time', 'unrealized', 'realized', 'pnl'])
        pd2 = pandas.DataFrame(portfolio_value, columns=['time', 'value'])
        import ipdb
        ipdb.set_trace()
        pd.set_index(['time'], inplace=True)
        pd2.set_index(['time'], inplace=True)

        # setup charting
        sns.set_style('darkgrid')
        fig = plt.figure(figsize=(13, 7))
        ax1 = fig.add_subplot(411)
        ax2 = fig.add_subplot(412)
        ax3 = fig.add_subplot(413)
        ax4 = fig.add_subplot(414)

        # plot algo performance
        pd2.plot(ax=ax1, y=['value'], legend=False, fontsize=5, rot=0)

        # plot up/down chart
        pd['pos'] = pd['pnl']
        pd['neg'] = pd['pnl']
        pd['pos'][pd['pos'] <= 0] = np.nan
        pd['neg'][pd['neg'] > 0] = np.nan
        pd.plot(ax=ax2, y=['pos', 'neg'], kind='area', stacked=False, color=['green', 'red'], legend=False, linewidth=0, fontsize=5, rot=0)
        ax2.set_ylabel('PnL')

        pd.plot(ax=ax3, y=['unrealized', 'realized', 'pnl'], kind='line', legend=False, fontsize=5, rot=0)
        ax3.legend(loc="upper left")

        # annotate with key data
        ax1.set_title('Performance')
        ax1.set_ylabel('Portfolio value($)')
        for xy in [portfolio_value[0][:2]] + [portfolio_value[-1][:2]]:
            ax1.annotate('$%s' % xy[1], xy=xy, textcoords='data')
            ax4.annotate('$%s' % xy[1], xy=xy, textcoords='data')

        # plot trade intent/trade action
        ax4.set_ylabel('Intent/Action')
        ax4.set_xlabel('Date')

        ax4.plot(trades)
        ax4.plot([x.time for x in requests if x.side == Side.BUY],
                 [x.price for x in requests if x.side == Side.BUY],
                 '2', color='y')
        ax4.plot([x.time for x in requests if x.side == Side.SELL],
                 [x.price for x in requests if x.side == Side.SELL],
                 '1', color='y')
        ax4.plot([x.time for x in responses if x.side == Side.BUY],  # FIXME
                 [x.price for x in responses if x.side == Side.BUY],
                 '^', color='g')
        ax4.plot([x.time for x in responses if x.side == Side.SELL],  # FIXME
                 [x.price for x in responses if x.side == Side.SELL],
                 'v', color='r')

        # set same limits
        y_bot, y_top = ax1.get_ylim()
        x_bot, x_top = ax1.get_xlim()
        ax1.set_xlim(x_bot, x_top)
        ax2.set_xlim(x_bot, x_top)
        ax3.set_xlim(x_bot, x_top)
        ax4.set_xlim(x_bot, x_top)
        dif = (x_top - x_bot) * .01
        ax1.set_xlim(x_bot - dif, x_top + dif)
        ax2.set_xlim(x_bot - dif, x_top + dif)
        ax3.set_xlim(x_bot - dif, x_top + dif)
        ax4.set_xlim(x_bot - dif, x_top + dif)
        plt.show()
