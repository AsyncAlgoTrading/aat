from typing import Optional
from aat import Strategy, Event, Order, Trade, Side, Instrument, InstrumentType


class MomentumStrategy(Strategy):
    def __init__(self,
                 instrument,
                 trigger,
                 profit,
                 stop,
                 notional=None,
                 enter_hour=10,
                 enter_minute=0,
                 exit_hour=15,
                 exit_minute=30,
                 *args, **kwargs) -> None:
        super(MomentumStrategy, self).__init__(*args, **kwargs)

        # symbol to trade
        self._symbol, self._symbol_type = instrument.split("-")

        # trigger the buy/sell
        self._trigger = abs(float(trigger) / 10000)

        # the point to take profit
        self._profit = abs(float(profit) / 10000)

        # the point to stop, can be any value < profit
        self._stop = float(stop) / 10000

        # how much to trade
        self._notional = float(notional) if notional else None
        self._quantity = None

        # only enter after this time
        self._enter_hour = enter_hour
        self._enter_minute = enter_minute

        # when to exit if havent stopped/taken profit
        self._exit_hour = exit_hour
        self._exit_minute = exit_minute

        # trackers
        self._initial_price = None
        self._initial_price_day = None
        self._last_price = None

        # orders
        self._enter_order: Optional[Order] = None
        self._enter_trade: Optional[Trade] = None
        self._exit_order: Optional[Order] = None

    async def onStart(self, event: Event) -> None:
        # Create an instrument
        inst = Instrument(name=self._symbol, type=InstrumentType(self._symbol_type))

        # Check that its available
        if inst not in self.instruments():
            raise Exception('Not available on exchange: {}'.format(self._symbol))

        # Subscribe
        await self.subscribe(inst)
        print('Subscribing to {}'.format(inst))

    async def onTrade(self, event: Event) -> None:
        '''Called whenever a `Trade` event is received'''
        trade: Trade = event.target  # type: ignore

        # set initial price to first trade
        if self._initial_price is None or self._initial_price == 0.0 or self._initial_price_day != trade.timestamp.day:
            self._initial_price = trade.price
            self._initial_price_day = trade.timestamp.day  # type: ignore

        # self last price to last traded price
        self._last_price = trade.price

        # determine if we trade
        cur_perf = (self._last_price - self._initial_price) / self._initial_price if self._initial_price != 0.0 else None  # type: ignore

        if cur_perf is None:
            # don't handle 0 price
            return

        if self._enter_trade is not None and self._exit_order is None:
            # already traded, look for exit
            if cur_perf > self._profit:
                # close position with sell
                print('exiting with sell order')
                self._exit_order = Order(side=Side.SELL,
                                         price=trade.price,
                                         volume=self._quantity,
                                         instrument=trade.instrument,
                                         order_type=Order.Types.MARKET,
                                         exchange=trade.exchange)
                await self.newOrder(self._exit_order)

            elif cur_perf < self._stop:
                # close to stop
                print('exiting to stop loss')
                side = Side.SELL if self._enter_order.side == Side.BUY else Side.BUY  # type: ignore
                self._exit_order = Order(side=side,
                                         price=trade.price,
                                         volume=self._quantity,
                                         instrument=trade.instrument,
                                         order_type=Order.Types.MARKET,
                                         exchange=trade.exchange)
                await self.newOrder(self._exit_order)

            else:
                # check if 15:45 or later
                if trade.timestamp.hour >= self._exit_hour and trade.timestamp.minute >= self._exit_minute:
                    # exit
                    print('exiting at EOD')
                    self._exit_order = Order(side=Side.SELL,
                                             price=trade.price,
                                             volume=self._quantity,
                                             instrument=trade.instrument,
                                             order_type=Order.Types.MARKET,
                                             exchange=trade.exchange)
                    await self.newOrder(self._exit_order)

        elif self._enter_trade is not None and self._exit_order is not None:
            # already ordered, wait for execution
            return

        elif self._enter_trade is None and self._exit_order is not None:
            raise Exception('Inconsistent state machine')

        else:
            if trade.timestamp.hour >= self._exit_hour and trade.timestamp.minute > self._exit_minute:
                # no more trading today
                return

            if trade.timestamp.hour <= self._enter_hour and trade.timestamp.minute < self._enter_minute:
                # no trading yet
                return

            if self._enter_order is not None:
                # already trying to enter, wait for execution
                return

            if cur_perf > self._trigger:
                # buy
                print('entering with buy order')
                if self._notional is not None:
                    self._quantity = max(self._notional // trade.price, 1)
                else:
                    self._quantity = 1  # type: ignore

                self._enter_order = Order(side=Side.BUY,
                                          price=trade.price,
                                          volume=self._quantity,
                                          instrument=trade.instrument,
                                          order_type=Order.Types.MARKET,
                                          exchange=trade.exchange)
                await self.newOrder(self._enter_order)

    async def onTraded(self, event: Event) -> None:
        trade: Trade = event.target  # type: ignore
        if self._exit_order is None:
            print('entered {} {:.2f} @ {:.2f}'.format(trade.instrument, trade.volume, trade.price))
            self._enter_trade = trade
            assert trade.my_order == self._enter_order
        else:
            print('exited {} {:.2f} @ {:.2f}'.format(trade.instrument, trade.volume, trade.price))
            self._enter_order = None
            self._enter_trade = None
            self._exit_order = None

            # reset initial price
            self._initial_price = trade.price

    async def onRejected(self, event: Event) -> None:
        print('order rejected')
        import sys
        sys.exit(0)

    async def onExit(self, event: Event) -> None:
        print('Finishing...')
        self.performanceCharts(save=True)
