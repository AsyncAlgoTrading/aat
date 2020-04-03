from ..strategy import TradingStrategy
from ..structs import MarketData, TradeRequest, TradeResponse
from ..enums import Side, OrderType
from ..logging import log


class SMAStrategy(TradingStrategy):
    def __init__(self, long: int = 20, short: int = 5, *args, **kwargs) -> None:
        super(SMAStrategy, self).__init__(*args, **kwargs)
        self.trades = []
        self.long = long
        self.short = short
        self.position = None

        self.golden = False

        self.long_average = 0.0
        self.short_average = 0.0

    def onFill(self, res: TradeResponse) -> None:
        if res.side == Side.BUY:
            log.info('d->g:bought %.2f @ %.2f' % (res.volume, res.price))
        else:
            log.info('g->d:sold %.2f @ %.2f' % (res.volume, res.price))

    def onTrade(self, data: MarketData) -> bool:
        self.trades.append(data)
        self.trades = self.trades[-1 * self.long:]
        long_average = self.calc_average(self.long)
        short_average = self.calc_average(self.short)

        if self.position is None:
            # was death, now golden
            if self.long_average > self.short_average and \
               long_average < short_average:
                req = TradeRequest(side=Side.BUY,
                                   volume=1,
                                   instrument=data.instrument,
                                   order_type=OrderType.MARKET,
                                   exchange=data.exchange,
                                   price=data.price,
                                   time=data.time)
                log.info("requesting buy : %s", req)
                self.position = self.request(req)
        else:
            # was golden, now death
            if self.long_average < self.short_average and \
               long_average > short_average:

                req = TradeRequest(side=Side.SELL,
                                   volume=1,
                                   instrument=data.instrument,
                                   order_type=OrderType.MARKET,
                                   exchange=data.exchange,
                                   price=data.price,
                                   time=data.time)
                log.info("requesting sell : %s", req)
                self.request(req)
                self.position = None

        self.long_average = long_average
        self.short_average = short_average

    def calc_average(self, count):
        calc = 0
        trades = self.trades[0 - count:]
        for t in trades:
            calc += t.price
        return calc / count

    def onError(self, e) -> None:
        log.critical(e)

    def onChange(self, data: MarketData) -> None:
        pass

    def onCancel(self, data: MarketData) -> None:
        pass

    def onOpen(self, data: MarketData) -> None:
        pass
