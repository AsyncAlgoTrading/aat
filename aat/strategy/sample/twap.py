from aat import Strategy, Event, Order, Trade, Side
from datetime import datetime, timedelta


class TimeWeightedAveragePrice(Strategy):
    def __init__(self, *args, **kwargs) -> None:
        '''Time Weighted Average Price Strategy

        Arguments:
            delay (int): time delay between orders
            target_volume (int): volume to be processed
            step (int): volume to process at each order
            start_time (str): time to start execution, converted to datetime
            end_time_offset (int): number of seconds past start_time to end orders after
            side (str): Buy/Sell side
            price_limit (int): price limit above trade price
        '''
        print(args)
        super(TimeWeightedAveragePrice, self).__init__()
        self.delay = int(args[0])
        self.target_volume = int(args[1])
        self.step = int(args[2])
        self.start_time = datetime.now() if args[3] == 'now' \
            else datetime.strptime(args[3], '%Y-%m-%d %H:%M:%S.%f')
        self.end_time = self.start_time + timedelta(seconds=int(args[4]))
        self.side = Side.BUY if args[5].lower() == 'buy' else Side.SELL
        self.price_limit = int(args[6])
        self.target_time = self.start_time
        self.volume_processed = 0
        self.volume_ordered = 0

    async def onStart(self, event: Event) -> None:
        self.subscribe(self.instruments()[0])

    async def onTrade(self, event: Event) -> None:
        '''Called whenever a `Trade` event is received'''
        trade: Trade = event.target  # type: ignore
        if self.volume_ordered < self.target_volume:
            now = datetime.now()
            if now >= self.target_time and now < self.end_time:
                req = Order(side=Side.BUY,
                            price=trade.price + self.price_limit,
                            volume=self.step,
                            instrument=trade.instrument,
                            order_type=Order.Types.MARKET,
                            exchange=trade.exchange)

                print("requesting : {}".format(req))
                self.target_time += timedelta(seconds=self.delay)
                self.volume_ordered += self.step
                await self.newOrder(req)
            else:
                print("Waiting for time window")
        else:
            print("Orders launched, do nothing! vol: {}".format(self.volume_processed))

    async def onBought(self, event: Event) -> None:
        trade: Trade = event.target  # type: ignore
        print('bought {:.2f} @ {:.2f}'.format(trade.volume, trade.price))
        self.volume_processed += trade.volume
        print('processed vol: {}'.format(self.volume_processed))

    async def onSold(self, event: Event) -> None:
        trade: Trade = event.target  # type: ignore
        print('bought {:.2f} @ {:.2f}'.format(trade.volume, trade.price))
        self.volume_processed += trade.volume
        print('processed vol: {}'.format(self.volume_processed))

    async def onReject(self, event: Event) -> None:
        print('order rejected')
        trade: Trade = event.target  # type: ignore
        self.volume_ordered -= trade.volume
        import sys
        sys.exit(0)

    def slippage(self, trade: Trade) -> Trade:
        # trade.slippage = trade.price * .0001  # .01% price impact TODO
        return trade

    def transactionCost(self, trade: Trade) -> Trade:
        # trade.transactionCost = trade.price * trade.volume * .0025  # 0.0025 max fee TODO
        return trade

    async def onExit(self, event: Event) -> None:
        print('Finishing...')
        import matplotlib.pyplot as plt  # type: ignore
        plt.plot(self.positions()[0].unrealizedPnlHistory)
        plt.show()
