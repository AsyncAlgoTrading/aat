from aat import Strategy, Event, Order, Trade, Side


class BuyAndHoldStrategy(Strategy):
    def __init__(self, *args, **kwargs) -> None:
        super(BuyAndHoldStrategy, self).__init__(*args, **kwargs)

    async def onTrade(self, event: Event) -> None:
        '''Called whenever a `Trade` event is received'''
        print('Trade:\n\t{}\n\tSlippage:{}\n\tTxnCost:{}'.format(event, event.target.slippage(), event.target.transactionCost()))

        # no past trades, no current orders
        if not self.orders(event.target.instrument) and not self.trades(event.target.instrument):
            # TODO await self.buy(...) ?
            req = Order(side=Side.BUY,
                        price=event.target.price + 10,
                        volume=1,
                        instrument=event.target.instrument,
                        order_type=Order.Types.MARKET,
                        exchange=event.target.exchange)
            print("requesting buy : {}".format(req))
            await self.newOrder(req)

        else:
            print(self.positions())
            print(self.risk())

    async def onBought(self, event: Event) -> None:
        print('bought {:.2f} @ {:.2f}'.format(event.target.volume, event.target.price))

    async def onReject(self, event: Event) -> None:
        print('order rejected')
        import sys
        sys.exit(0)

    def slippage(self, trade: Trade) -> Trade:
        slippage = trade.price * .0001  # .01% price impact
        trade.addSlippage(slippage)
        return trade

    def transactionCost(self, trade: Trade) -> Trade:
        txncost = trade.price * trade.volume * .0025  # 0.0025 max fee
        trade.addTransactionCost(txncost)
        return trade
