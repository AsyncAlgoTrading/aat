from aat.core import Event
from aat.strategy import Strategy


class BuyAndHoldStrategy(Strategy):
    def __init__(self, *args, **kwargs) -> None:
        super(BuyAndHoldStrategy, self).__init__(*args, **kwargs)
        self.bought = {}

    def onTrade(self, event: Event):
        '''Called whenever a `Trade` event is received'''
        print('Trade:', event)
        # if event.target.instrument not in self.bought:
        #     req = TradeRequest(side=Side.BUY,
        #                        volume=1,
        #                        instrument=data.instrument,
        #                        order_type=OrderType.MARKET,
        #                        exchange=data.exchange,
        #                        price=data.price,
        #                        time=data.time)
        #     log.info("requesting buy : %s", req)
        #     self.request(req)
        #     self.bought[data.instrument] = 'pending'

    # def onFill(self, res: TradeResponse) -> None:
    #     self.bought[res.instrument] = res
    #     log.info('bought %.2f @ %.2f' % (res.volume, res.price))

    # def slippage(self, resp: TradeResponse) -> TradeResponse:
    #     slippage = resp.price * .0001  # .01% price impact
    #     if resp.side == Side.BUY:
    #         # price moves against (up)
    #         resp.slippage = slippage
    #         resp.price += slippage
    #     else:
    #         # price moves against (down)
    #         resp.slippage = -slippage
    #         resp.price -= slippage
    #     return resp

    # def transactionCost(self, resp: TradeResponse) -> TradeResponse:
    #     txncost = resp.price * resp.volume * .0025  # gdax is 0.0025 max fee
    #     if resp.side == Side.BUY:
    #         # price moves against (up)
    #         resp.transaction_cost = txncost
    #         resp.price += txncost
    #     else:
    #         # price moves against (down)
    #         resp.transaction_cost = -txncost
    #         resp.price -= txncost
    #     return resp
