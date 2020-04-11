from typing import Any, Dict
from aat import Strategy, Event, Order, Side


class BuyAndHoldStrategy(Strategy):
    def __init__(self, *args, **kwargs) -> None:
        super(BuyAndHoldStrategy, self).__init__(*args, **kwargs)
        self._bought: Dict[str, Any] = {}

    def onTrade(self, event: Event) -> None:
        '''Called whenever a `Trade` event is received'''
        print('Trade:\n\t{}\n\tSlippage:{}\n\tTxnCost:{}'.format(event, event.target.slippage(), event.target.transactionCost()))
        if event.target.instrument not in self._bought and not self.openOrders(event.target.instrument):
            # TODO await self.buy(...) ?
            req = Order(side=Side.BUY,
                        price=event.target.price,
                        volume=1,
                        instrument=event.target.instrument,
                        order_type=Order.Types.MARKET,
                        exchange=event.target.exchange)
            print("requesting buy : {}".format(req))
            self.request(req)

    def onError(self, event: Event) -> None:
        print("Error:", event)

    def onBought(self, event: Event) -> None:
        print('bought {.2f} @ {.2f}'.format(event.target.volume, event.target.price))
        self._bought[event.target.instrument] = event.target

    def slippage(self, order: Order) -> Order:
        slippage = order.price * .0001  # .01% price impact
        if order.side == Side.BUY:
            # price moves against (up)
            order.slippage = slippage
            order.price += slippage
        else:
            # price moves against (down)
            order.slippage = -slippage
            order.price -= slippage
        return order

    def transactionCost(self, order: Order) -> Order:
        txncost = order.price * order.volume * .0025  # 0.0025 max fee
        if order.side == Side.BUY:
            # price moves against (up)
            order.transaction_cost = txncost
            order.price += txncost
        else:
            # price moves against (down)
            order.transaction_cost = -txncost
            order.price -= txncost
        return order
