from ..strategy import TradingStrategy
from ..structs import MarketData, TradeRequest, TradeResponse
from ..enums import Side, TradeResult, OrderType
from ..logging import STRAT as slog, ERROR as elog


class SMACrossesStrategy(TradingStrategy):
    def __init__(self, size_short: int, size_long: int) -> None:
        super(SMACrossesStrategy, self).__init__()
        self.short = size_short
        self.shorts = []
        self.short_av = 0.0

        self.long = size_long
        self.longs = []
        self.long_av = 0.0

        self.prev_state = ''
        self.state = ''

        self.bought = 0.0
        self.bought_qty = 0.0
        self.profits = 0.0

        self._intitialvalue = None
        self._portfolio_value = []

    def onBuy(self, res: TradeResponse) -> None:
        if not res.status == TradeResult.FILLED:
            slog.info('order failure: %s' % res)
            return

        if self._intitialvalue is None:
            date = res.time
            self._intitialvalue = (date, res.volume*res.price)
            self._portfolio_value.append(self._intitialvalue)

        self.bought = res.volume*res.price
        self.bought_qty = res.volume
        slog.info('d->g:bought %.2f @ %.2f for %.2f ---- %.2f %.2f' % (res.volume, res.price, self.bought, self.short_av, self.long_av))

    def onSell(self, res: TradeResponse) -> None:
        if not res.status == TradeResult.FILLED:
            slog.info('order failure: %s' % res)
            return

        sold = res.volume*res.price
        profit = sold - self.bought
        self.profits += profit
        slog.info('g->d:sold %.2f @ %.2f for %.2f - %.2f - %.2f ---- %.2f %.2f' % (res.volume, res.price, sold, profit, self.profits, self.short_av, self.long_av))
        self.bought = 0.0
        self.bought_qty = 0.0

        date = res.time
        self._portfolio_value.append((
                date,
                self._portfolio_value[-1][1] + profit))

    def onTrade(self, data: MarketData) -> bool:
        # add data to arrays
        self.shorts.append(data.price)
        self.longs.append(data.price)

        # check requirements
        if len(self.shorts) > self.short:
            self.shorts.pop(0)

        if len(self.longs) > self.long:
            self.longs.pop(0)

        # calc averages
        self.short_av = float(sum(self.shorts)) / max(len(self.shorts), 1)
        self.long_av = float(sum(self.longs)) / max(len(self.longs), 1)

        slog.info('%.2f %.2f', self.short_av, self.long_av)
        # sell out if losing too much
        stoploss = (self.bought - data.price*self.bought_qty) > 5
        # stoploss = False

        self.prev_state = self.state
        if self.short_av > self.long_av:
            # buying
            self.state = 'golden'
        elif self.short_av < self.long_av or stoploss:
            # selling
            self.state = 'death'
        else:
            self.state = ''

        if len(self.longs) < self.long or len(self.shorts) < self.short:
            return False

        if self.state == 'golden' and self.prev_state != 'golden' and \
                self.bought == 0.0:  # watch for floating point error
            req = TradeRequest(side=Side.BUY,
                               # buy between .2 and 1 BTC
                               volume=max(min(1.0, data.volume), .2),
                               instrument=data.instrument,
                               order_type=OrderType.MARKET,
                               price=data.price)
            # slog.info("requesting buy : %s", req)
            self.requestBuy(self.onBuy, req)
            return True

        elif self.state == 'death' and self.prev_state != 'death' and \
                self.bought > 0.0:
            req = TradeRequest(side=Side.SELL,
                               volume=self.bought_qty,
                               instrument=data.instrument,
                               order_type=OrderType.MARKET,
                               price=data.price)
            # slog.info("requesting sell : %s", req)
            self.requestSell(self.onSell, req)
            return True

        return False

    def onError(self, e) -> None:
        elog.critical(e)

    def onAnalyze(self, _) -> None:
        import pandas
        import matplotlib.pyplot as plt
        import seaborn as sns

        # pd = pandas.DataFrame(self._actions,
        #                       columns=['time', 'action', 'price'])

        pd = pandas.DataFrame(self._portfolio_value, columns=['time', 'value'])
        pd.set_index(['time'], inplace=True)

        print(self.short, self.long, pd.iloc[1].value, pd.iloc[-1].value)
        # sp500 = pandas.DataFrame()
        # tmp = pandas.read_csv('./data/sp/sp500_v_kraken.csv')
        # sp500['Date'] = pandas.to_datetime(tmp['Date'])
        # sp500['Close'] = tmp['Close']
        # sp500.set_index(['Date'], inplace=True)
        # print(sp500)

        sns.set_style('darkgrid')
        fig, ax1 = plt.subplots()

        plt.title('BTC algo 1 performance - %d-%d Momentum ' % (self.short, self.long))
        ax1.plot(pd)

        ax1.set_ylabel('Portfolio value($)')
        ax1.set_xlabel('Date')
        for xy in [self._portfolio_value[0]] + [self._portfolio_value[-1]]:
            ax1.annotate('$%s' % xy[1], xy=xy, textcoords='data')

        # ax2 = ax1.twinx()
        # ax2.plot(sp500, 'r')
        # ax2.set_ylabel('S&P500 ($)')

        plt.show()

    def onChange(self, data: MarketData) -> None:
        pass

    def onContinue(self, data: MarketData) -> None:
        pass

    def onDone(self, data: MarketData) -> None:
        pass

    def onHalt(self, data: MarketData) -> None:
        pass

    def onOpen(self, data: MarketData) -> None:
        pass

    def onReceived(self, data: MarketData) -> None:
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
