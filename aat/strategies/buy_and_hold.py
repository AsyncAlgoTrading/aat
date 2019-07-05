from ..strategy import TradingStrategy
from ..structs import MarketData, TradeRequest, TradeResponse
from ..enums import Side, OrderType
from ..logging import log


class BuyAndHoldStrategy(TradingStrategy):
    def __init__(self, *args, **kwargs) -> None:
        super(BuyAndHoldStrategy, self).__init__(*args, **kwargs)
        self.bought = {}

    def onFill(self, res: TradeResponse) -> None:
        self.bought[res.instrument] = res
        log.info('bought %.2f @ %.2f' % (res.volume, res.price))

    def onTrade(self, data: MarketData) -> bool:
        if data.instrument not in self.bought:
            req = TradeRequest(side=Side.BUY,
                               volume=1,
                               instrument=data.instrument,
                               order_type=OrderType.MARKET,
                               exchange=data.exchange,
                               price=data.price,
                               time=data.time)
            log.info("requesting buy : %s", req)
            self.request(req)
            self.bought[data.instrument] = 'pending'

    def onError(self, e) -> None:
        log.critical(e)

    def onChange(self, data: MarketData) -> None:
        pass

    def onCancel(self, data: MarketData) -> None:
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
    def __init__(self, *args, **kwargs) -> None:
        super(BuyAndHoldStrategy2, self).__init__(*args, **kwargs)
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
            self.request(req)
            self.sold = 'pending'

    def onError(self, e) -> None:
        log.critical(e)

    def onChange(self, data: MarketData) -> None:
        pass

    def onCancel(self, data: MarketData) -> None:
        pass

    def onOpen(self, data: MarketData) -> None:
        pass
