from ..strategy import TradingStrategy
from ..structs import MarketData, TradeRequest, TradeResponse
from ..enums import Side, OrderType
from ..logging import log


class BuyAndHoldStrategy(TradingStrategy):
    def __init__(self) -> None:
        super(BuyAndHoldStrategy, self).__init__()
        self.bought = None

    def onFill(self, res: TradeResponse) -> None:
        self.bought = res
        log.info('d->g:bought %.2f @ %.2f' % (res.volume, res.price))

    def onTrade(self, data: MarketData) -> bool:
        if self.bought is None:
            req = TradeRequest(side=Side.BUY,
                               volume=1,
                               instrument=data.instrument,
                               order_type=OrderType.MARKET,
                               exchange=data.exchange,
                               price=data.price,
                               time=data.time)
            log.info("requesting buy : %s", req)
            self.requestBuy(req)
            self.bought = 'pending'

    def onError(self, e) -> None:
        log.critical(e)

    def onAnalyze(self, engine) -> None:
        import pandas
        import numpy as np
        import matplotlib, matplotlib.pyplot as plt  # noqa: E401
        import seaborn as sns
        matplotlib.rc('font', **{'size': 5})

        # extract data from trading engine
        portfolio_value = engine.portfolio_value()
        requests = engine.query().query_tradereqs()
        responses = engine.query().query_traderesps()
        trades = pandas.DataFrame([{'time': x.time, 'price': x.price} for x in engine.query().query_trades(instrument=requests[0].instrument, page=None)])
        trades.set_index(['time'], inplace=True)

        # format into pandas
        pd = pandas.DataFrame(portfolio_value, columns=['time', 'value', 'pnl'])
        pd.set_index(['time'], inplace=True)

        # setup charting
        sns.set_style('darkgrid')
        fig = plt.figure()
        ax1 = fig.add_subplot(311)
        ax2 = fig.add_subplot(312)
        ax3 = fig.add_subplot(313)

        # plot algo performance
        pd.plot(ax=ax1, y=['value'], legend=False, fontsize=5, rot=0)

        # plot up/down chart
        pd['pos'] = pd['pnl']
        pd['neg'] = pd['pnl']
        pd['pos'][pd['pos'] <= 0] = np.nan
        pd['neg'][pd['neg'] > 0] = np.nan
        pd.plot(ax=ax2, y=['pos', 'neg'], kind='area', stacked=False, color=['green', 'red'], legend=False, linewidth=0, fontsize=5, rot=0)

        # annotate with key data
        ax1.set_title('Performance')
        ax1.set_ylabel('Portfolio value($)')
        for xy in [portfolio_value[0][:2]] + [portfolio_value[-1][:2]]:
            ax1.annotate('$%s' % xy[1], xy=xy, textcoords='data')
            ax3.annotate('$%s' % xy[1], xy=xy, textcoords='data')

        # plot trade intent/trade action
        ax3.set_ylabel('Intent/Action')
        ax3.set_xlabel('Date')

        ax3.plot(trades)
        ax3.plot([x.time for x in requests if x.side == Side.BUY],
                 [x.price for x in requests if x.side == Side.BUY],
                 '2', color='y')
        ax3.plot([x.time for x in requests if x.side == Side.SELL],
                 [x.price for x in requests if x.side == Side.SELL],
                 '1', color='y')
        ax3.plot([x.time for x in responses if x.side == Side.BUY],  # FIXME
                 [x.price for x in responses if x.side == Side.BUY],
                 '^', color='g')
        ax3.plot([x.time for x in responses if x.side == Side.SELL],  # FIXME
                 [x.price for x in responses if x.side == Side.SELL],
                 'v', color='r')

        # set same limits
        y_bot, y_top = ax1.get_ylim()
        x_bot, x_top = ax1.get_xlim()
        ax3.set_ylim(y_bot, y_top)
        ax1.set_xlim(x_bot, x_top)
        ax2.set_xlim(x_bot, x_top)
        ax3.set_xlim(x_bot, x_top)
        dif = (x_top-x_bot)*.01
        ax1.set_xlim(x_bot-dif, x_top+dif)
        ax2.set_xlim(x_bot-dif, x_top+dif)
        ax3.set_xlim(x_bot-dif, x_top+dif)
        plt.show()

    def onChange(self, data: MarketData) -> None:
        pass

    def onContinue(self, data: MarketData) -> None:
        pass

    def onCancel(self, data: MarketData) -> None:
        pass

    def onHalt(self, data: MarketData) -> None:
        pass

    def onOpen(self, data: MarketData) -> None:
        pass

    def slippage(self, resp: TradeResponse) -> TradeResponse:
        slippage = resp.price * .0001  # .01% price impact
        if resp.side == Side.BUY:
            # price moves against (up)
            resp.slippage = slippage
            resp.price += slippage
        else:
            # price moves against (down)
            resp.slippage = -slippage
            resp.price -= slippage
        return resp

    def transactionCost(self, resp: TradeResponse) -> TradeResponse:
        txncost = resp.price * resp.volume * .0025  # gdax is 0.0025 max fee
        if resp.side == Side.BUY:
            # price moves against (up)
            resp.transaction_cost = txncost
            resp.price += txncost
        else:
            # price moves against (down)
            resp.transaction_cost = -txncost
            resp.price -= txncost
        return resp


class BuyAndHoldStrategy2(TradingStrategy):
    def __init__(self) -> None:
        super(BuyAndHoldStrategy2, self).__init__()
        self.sold = None

    def onFill(self, res: TradeResponse) -> None:
        self.sold = res
        log.info('d->g:sold %.2f @ %.2f' % (res.volume, res.price))

    def onTrade(self, data: MarketData) -> bool:
        if self.sold is None:
            req = TradeRequest(side=Side.SELL,
                               volume=.1,
                               instrument=data.instrument,
                               order_type=OrderType.LIMIT,
                               exchange=data.exchange,
                               price=data.price,
                               time=data.time)
            log.info("requesting sell : %s", req)
            self.requestSell(req)
            self.sold = 'pending'

    def onError(self, e) -> None:
        log.critical(e)

    def onChange(self, data: MarketData) -> None:
        pass

    def onCancel(self, data: MarketData) -> None:
        pass

    def onOpen(self, data: MarketData) -> None:
        pass
