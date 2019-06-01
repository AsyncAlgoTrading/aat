from ..strategy import TradingStrategy
from ..structs import MarketData, TradeRequest, TradeResponse
from ..enums import Side, OrderType
from ..logging import STRAT as slog, ERROR as elog


class BuyAndHoldStrategy(TradingStrategy):
    def __init__(self) -> None:
        super(BuyAndHoldStrategy, self).__init__()
        self.bought = None

    def onBuy(self, res: TradeResponse) -> None:
        self.bought = res
        slog.info('d->g:bought %.2f @ %.2f' % (res.volume, res.price))

    def onSell(self, res: TradeResponse) -> None:
        pass

    def onTrade(self, data: MarketData) -> bool:
        # add data to arrays
        if self.bought is None:
            req = TradeRequest(side=Side.BUY,
                               volume=1.0,
                               instrument=data.instrument,
                               order_type=OrderType.MARKET,
                               exchange=data.exchange,
                               price=data.price,
                               time=data.time)
            slog.info("requesting buy : %s", req)
            self.requestBuy(self.onBuy, req)
            return True
        return False

    def onError(self, e) -> None:
        elog.critical(e)

    def onAnalyze(self, engine) -> None:
        import pandas
        import matplotlib.pyplot as plt
        import seaborn as sns

        portfolio_value = engine.portfolio_value()
        requests = engine.query().query_tradereqs()
        responses = engine.query().query_traderesps()
        trades = pandas.DataFrame([{'time': x.time, 'price': x.price} for x in engine.query().query_trades(instrument=requests[0].instrument, page=None)])
        trades.set_index(['time'], inplace=True)

        pd = pandas.DataFrame(portfolio_value, columns=['time', 'value'])
        pd.set_index(['time'], inplace=True)

        sns.set_style('darkgrid')
        fig = plt.figure(figsize=(5, 8))
        ax1 = fig.add_subplot(211)
        ax2 = fig.add_subplot(212)

        plt.title('BTC algo 1 performance')
        ax1.plot(pd)

        ax1.set_title('Performance')
        ax1.set_ylabel('Portfolio value($)')
        for xy in [portfolio_value[0]] + [portfolio_value[-1]]:
            ax1.annotate('$%s' % xy[1], xy=xy, textcoords='data')
            ax2.annotate('$%s' % xy[1], xy=xy, textcoords='data')

        ax2.set_title('Trades')
        ax2.set_ylabel('Intent/Action')
        ax2.set_xlabel('Date')

        ax2.plot([x.time for x in requests if x.side == Side.BUY],
                 [x.price for x in requests if x.side == Side.BUY],
                 '2', color='y')
        ax2.plot([x.time for x in requests if x.side == Side.SELL],
                 [x.price for x in requests if x.side == Side.SELL],
                 '1', color='y')
        ax2.plot([x.time for x in responses if x.side == Side.BUY],  # FIXME
                 [x.price for x in responses if x.side == Side.BUY],
                 '^', color='g')
        ax2.plot([x.time for x in responses if x.side == Side.SELL],  # FIXME
                 [x.price for x in responses if x.side == Side.SELL],
                 'v', color='r')
        ax2.plot(trades)

        y_bot, y_top = ax1.get_ylim()
        x_bot, x_top = ax1.get_xlim()
        ax2.set_ylim(y_bot, y_top)
        ax2.set_xlim(x_bot, x_top)

        plt.show()

        print(requests)
        print(responses)

    def onChange(self, data: MarketData) -> None:
        pass

    def onContinue(self, data: MarketData) -> None:
        pass

    def onFill(self, data: MarketData) -> None:
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
