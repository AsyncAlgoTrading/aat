import numpy
from ..strategy import TradingStrategy
from ..structs import MarketData, TradeRequest, TradeResponse
from ..enums import Side, OrderType
from ..logging import STRAT as slog, ERROR as elog


class CustomStrategy(TradingStrategy):
    def __init__(self, size: int) -> None:
        super(CustomStrategy, self).__init__()
        self.size = size
        self.ticks = []

        self.x = numpy.arange(0, self.size)
        self.prev_state = ''
        self.state = ''

        self.bought = 0.0
        self.bought_qty = 0.0
        self.profits = 0.0

    def onBuy(self, res: TradeResponse) -> None:
        self.bought = res.volume*res.price
        self.bought_qty = res.volume
        slog.info('d->g:bought %.2f @ %.2f for %.2f', res.volume, res.price, self.bought)

    def onSell(self, res: TradeResponse) -> None:
        sold = res.volume*res.price
        profit = sold - self.bought
        self.profits += profit

        slog.info('g->d:sold %.2f @ %.2f for %.2f - %.2f - %.2f', res.volume, res.price, sold, profit, self.profits)

        self.bought = 0.0
        self.bought_qty = 0.0

    def onTrade(self, data: MarketData):
        # add data to arrays
        self.ticks.append(data.price)

        # check requirements
        if len(self.ticks) > self.size:
            self.ticks.pop(0)

        # ready?
        if len(self.ticks) < self.size:
            return False

        y = numpy.array(self.ticks)
        z = numpy.polyfit(self.x, y, 1)  # linreg

        shouldbuy = z[0] > .2
        shouldsell = z[0] < .2

        # sell out if losing too much
        # stoploss = (self.bought - data.price*self.bought_qty) > 5
        stoploss = False

        self.prev_state = self.state
        if shouldbuy:
            # buying
            self.state = 'buy'
        elif shouldsell or stoploss:
            # selling
            self.state = 'sell'
        else:
            self.state = ''

        if self.state == 'buy' and self.prev_state != 'buy' and \
                self.bought == 0.0:  # watch for floating point  error
            req = TradeRequest(side=Side.BUY,
                               # buy between .2 and 1 BTC
                               volume=max(min(1.0, data.volume), .2),
                               instrument=data.instrument,
                               price=data.price,
                               order_type=OrderType.MARKET,
                               time=data.time)
            self.requestBuy(self.onBuy, req)
            return True

        elif self.state == 'sell' and self.prev_state != 'sell' and \
                self.bought > 0.0:
            req = TradeRequest(side=Side.SELL,
                               volume=self.bought_qty,
                               instrument=data.instrument,
                               price=data.price,
                               order_type=OrderType.MARKET,
                               time=data.time)
            self.requestSell(self.onSell, req)
            return True

        return False

    def onError(self, e: MarketData):
        elog.critical(e)

    def onAnalyze(self, engine) -> None:
        import pandas
        import matplotlib.pyplot as plt
        import seaborn as sns

        portfolio_value = engine.portfolio_value()
        requests = engine.query().query_tradereqs()
        trades = pandas.DataFrame([{'time': x.time, 'price': x.price} for x in engine.query().query_trades(instrument=requests[0].instrument, page=None)])
        trades.set_index(['time'], inplace=True)

        pd = pandas.DataFrame(portfolio_value, columns=['time', 'value'])
        pd.set_index(['time'], inplace=True)

        print(self.size, pd.iloc[1].value, pd.iloc[-1].value)

        sns.set_style('darkgrid')
        fig, ax1 = plt.subplots()

        # plt.title('BTC algo 1 performance - %d-%d Momentum ' % (self.short, self.long))
        ax1.plot(pd)

        ax1.set_ylabel('Portfolio value($)')
        ax1.set_xlabel('Date')
        for xy in [portfolio_value[0]] + [portfolio_value[-1]]:
            ax1.annotate('$%s' % xy[1], xy=xy, textcoords='data')

        plt.show()

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
