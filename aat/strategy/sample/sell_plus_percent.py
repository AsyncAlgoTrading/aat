import math
from typing import Dict, Tuple

from aat import Strategy, Event, Order, Trade, Side, Instrument


class SellPlusPercentStrategy(Strategy):
    def __init__(self, percent=10, *args, **kwargs) -> None:
        super(SellPlusPercentStrategy, self).__init__(*args, **kwargs)

        self._up_percent = 1.0 + float(percent) / 100
        self._down_percent = 1.0 - float(percent) / 100
        self._stop: Dict[Instrument, Tuple[float, float, float]] = {}

    async def onStart(self, event: Event) -> None:
        pos = self.positions()
        print("positions: {}".format(pos))

    async def onTrade(self, event: Event) -> None:
        '''Called whenever a `Trade` event is received'''
        trade: Trade = event.target  # type: ignore

        # no current orders, no past trades
        if not self.orders(trade.instrument) and not self.trades(trade.instrument):
            req = Order(side=Side.BUY,
                        price=trade.price,
                        volume=math.ceil(1000 / trade.price),
                        instrument=trade.instrument,
                        exchange=trade.exchange)

            print('requesting buy : {}'.format(req))
            await self.newOrder(req)

        else:
            # no current orders, 1 past trades, and stop set
            if not self.orders(trade.instrument) and len(self.trades(trade.instrument)) == 1 and \
                    trade.instrument in self._stop and \
                    (trade.price >= self._stop[trade.instrument][0] or
                     trade.price <= self._stop[trade.instrument][1]):
                req = Order(side=Side.SELL,
                            price=trade.price,
                            volume=self._stop[trade.instrument][2],
                            instrument=trade.instrument,
                            exchange=trade.exchange)

                print('requesting sell : {}'.format(req))
                await self.newOrder(req)

    async def onBought(self, event: Event) -> None:
        trade: Trade = event.target  # type: ignore

        print('bought {} {:.2f} @ {:.2f}'.format(trade.instrument, trade.volume, trade.price))
        self._stop[trade.instrument] = (trade.price * self._up_percent,
                                        trade.price * self._down_percent,
                                        trade.volume)

    async def onSold(self, event: Event) -> None:
        trade: Trade = event.target  # type: ignore
        print('sold {:.2f} @ {:.2f}'.format(trade.volume, trade.price))
        del self._stop[trade.instrument]

    async def onRejected(self, event: Event) -> None:
        print('order rejected')
        import sys
        sys.exit(0)

    async def onExit(self, event: Event) -> None:
        print('Finishing...')
        # self.performanceCharts()
