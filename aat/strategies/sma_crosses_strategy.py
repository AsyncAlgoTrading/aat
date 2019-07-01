from ..strategy import TradingStrategy
from ..structs import MarketData, TradeRequest, TradeResponse
from ..enums import Side, TradeResult, OrderType
from ..logging import log


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

    def onBuy(self, res: TradeResponse) -> None:
        if not res.status == TradeResult.FILLED:
            log.info('order failure: %s' % res)
            return

        self.bought = res.volume*res.price
        self.bought_qty = res.volume
        log.info('d->g:bought %.2f @ %.2f for %.2f ---- %.2f %.2f' % (res.volume, res.price, self.bought, self.short_av, self.long_av))

    def onSell(self, res: TradeResponse) -> None:
        if not res.status == TradeResult.FILLED:
            log.info('order failure: %s' % res)
            return

        sold = res.volume*res.price
        profit = sold - self.bought
        self.profits += profit
        log.info('g->d:sold %.2f @ %.2f for %.2f - %.2f - %.2f ---- %.2f %.2f' % (res.volume, res.price, sold, profit, self.profits, self.short_av, self.long_av))
        self.bought = 0.0
        self.bought_qty = 0.0

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

        log.info('%.2f %.2f', self.short_av, self.long_av)
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
            return

        if self.state == 'golden' and self.prev_state != 'golden' and \
                self.bought == 0.0:  # watch for floating point error
            req = TradeRequest(side=Side.BUY,
                               # buy between .2 and 1 BTC
                               volume=max(min(1.0, data.volume), .2),
                               instrument=data.instrument,
                               order_type=OrderType.MARKET,
                               exchange=data.exchange,
                               price=data.price,
                               time=data.time)
            # log.info("requesting buy : %s", req)
            self.requestBuy(self.onBuy, req)

        elif self.state == 'death' and self.prev_state != 'death' and \
                self.bought > 0.0:
            req = TradeRequest(side=Side.SELL,
                               volume=self.bought_qty,
                               instrument=data.instrument,
                               order_type=OrderType.MARKET,
                               exchange=data.exchange,
                               price=data.price,
                               time=data.time)
            # log.info("requesting sell : %s", req)
            self.requestSell(self.onSell, req)

    def onError(self, e) -> None:
        log.critical(e)

    def onAnalyze(self, engine) -> None:
        import pandas
        import matplotlib.pyplot as plt
        import seaborn as sns
        portfolio_value = engine.portfolio_value()
        requests = engine.query().query_tradereqs()
        responses = engine.query().query_traderesps()

        pd = pandas.DataFrame(portfolio_value, columns=['time', 'value'])
        pd.set_index(['time'], inplace=True)

        if len(requests) > 0:
            trades = pandas.DataFrame([{'time': x.time, 'price': x.price} for x in engine.query().query_trades(instrument=requests[0].instrument, page=None)])
            trades.set_index(['time'], inplace=True)

        if pd.size > 0:
            print(self.short, self.long, pd.iloc[1].value, pd.iloc[-1].value)
            sns.set_style('darkgrid')
            fig, ax1 = plt.subplots()

            plt.title('BTC algo 1 performance - %d-%d Momentum ' % (self.short, self.long))
            ax1.plot(pd)

            ax1.set_ylabel('Portfolio value($)')
            ax1.set_xlabel('Date')
            for xy in [portfolio_value[0]] + [portfolio_value[-1]]:
                ax1.annotate('$%s' % xy[1], xy=xy, textcoords='data')
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
