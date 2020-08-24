from aat import Strategy, Event, Order, Trade, Side, Instrument, InstrumentType


class MomentumStrategy(Strategy):
    def __init__(self, instrument, trigger, profit, stop, quantity=1, buy_only=True, *args, **kwargs) -> None:
        super(MomentumStrategy, self).__init__(*args, **kwargs)

        # symbol to trade
        self._symbol, self._symbol_type = instrument.split("-")

        # trigger the buy/sell
        self._trigger = abs(float(trigger) / 10000)

        # the point to take profit
        self._profit = abs(float(profit) / 10000)

        # the point to stop, can be any value < profit
        self._stop = abs(float(stop) / 10000)

        # do we also short?
        self._buy_only = buy_only

        # how much to trade
        self._quantity = quantity

        # trackers
        self._initial_price = None
        self._last_price = None

        # orders
        self._enter_order = None
        self._enter_trade = None
        self._exit_order = None

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
        if self._initial_price is None or self._initial_price == 0.0:
            self._initial_price = trade.price

        # self last price to last traded price
        self._last_price = trade.price

        # determine if we trade
        cur_perf = (self._last_price - self._initial_price) / self._initial_price if self._initial_price != 0.0 else None

        print(cur_perf)
        if cur_perf is None:
            # don't handle 0 price
            return

        if self._enter_trade is not None and self._exit_order is not None:
            # already traded, look for exit
            if cur_perf > self._profit:
                # close position with sell
                self._exit_order = Order(side=Side.SELL,
                                         price=trade.price,
                                         volume=self._quantity,
                                         instrument=trade.instrument,
                                         order_type=Order.Types.MARKET,
                                         exchange=trade.exchange)
                await self.newOrder(self._exit_order)
            elif self._enter_order.side == Side.SELL and cur_perf < -1 * self._profit:
                # close position with buy
                self._exit_order = Order(side=Side.BUY,
                                         price=trade.price,
                                         volume=self._quantity,
                                         instrument=trade.instrument,
                                         order_type=Order.Types.MARKET,
                                         exchange=trade.exchange)
                await self.newOrder(self._exit_order)

            elif abs(cur_perf) < self._stop or cur_perf > -1 * self._stop:
                # close to stop
                side = Side.SELL if self._enter_order.side == Side.BUY else Side.BUY
                self._exit_order = Order(side=side,
                                         price=trade.price,
                                         volume=self._quantity,
                                         instrument=trade.instrument,
                                         order_type=Order.Types.MARKET,
                                         exchange=trade.exchange)
                await self.newOrder(self._exit_order)

            else:
                # check if 15:45 or later
                # TODO

                pass

        elif self._enter_order is not None:
            # already ordered, wait for execution
            return

        elif self._exit_order is not None:
            raise Exception('Inconsistent state machine')

        else:
            # TODO don't do this if later than 15:45

            if cur_perf > self._trigger:
                # buy
                self._enter_order = Order(side=Side.BUY,
                                          price=trade.price,
                                          volume=self._quantity,
                                          instrument=trade.instrument,
                                          order_type=Order.Types.MARKET,
                                          exchange=trade.exchange)
                await self.newOrder(self._enter_order)

            elif cur_perf < -1 * self._trigger and not self._buy_only:
                # short
                self._enter_order = Order(side=Side.SELL,
                                          price=trade.price,
                                          volume=self._quantity,
                                          instrument=trade.instrument,
                                          order_type=Order.Types.MARKET,
                                          exchange=trade.exchange)
                await self.newOrder(self._enter_order)

            else:
                return

    async def onTraded(self, event: Event) -> None:
        trade: Trade = event.target  # type: ignore
        print('bought {} {:.2f} @ {:.2f}'.format(trade.instrument, trade.volume, trade.price))
        if self._exit_order is None:
            self._enter_trade = trade
            assert trade.my_order == self._enter_order
        else:
            self._enter_order = None
            self._enter_trade = None
            self._exit_order = None

    async def onRejected(self, event: Event) -> None:
        print('order rejected')
        import sys
        sys.exit(0)

    async def onExit(self, event: Event) -> None:
        print('Finishing...')
        self.performanceCharts()
