import asyncio
import numpy as np  # type: ignore
import string
from datetime import datetime, timedelta
from collections import deque
from random import choice, random, randint
from typing import AsyncIterator, Deque, Iterator, List, Set
from ..exchange import Exchange
from ...core import Instrument, OrderBook, Order, Event, ExchangeType, Position
from ...config import TradingType, Side, EventType, OrderType


def _getName(n: int = 1) -> List[str]:
    columns = [
        "".join(np.random.choice(list(string.ascii_uppercase), choice((1, 2, 3, 4))))
        + "."
        + "".join(np.random.choice(list(string.ascii_uppercase), choice((1, 2))))
        for _ in range(n)
    ]
    return columns


class SyntheticExchange(Exchange):
    _inst = 0

    def __init__(
        self,
        trading_type: TradingType = None,
        verbose: bool = False,
        inst_count: int = 3,
        cycles: int = 10000,
        positions: bool = False,
    ) -> None:
        """A synthetic exchange. Runs a limit order book for a number of randomly generated assets,
        takes random walks.

        Args:
            trading_type (TradingType); Trading type. Should be in (SIMULATION, BACKTEST)
            verbose (bool); run in verbose mode (prints order books every tick)
            inst_count (int); number of random instruments to use
            cycles (int); number of random cycles to go through, each cycle
                          it will randomly generate an order event.
            positions (bool); randomly generate starting positions
        """
        super().__init__(ExchangeType("synthetic{}".format(SyntheticExchange._inst)))
        print("using synthetic exchange: {}".format(self.exchange()))

        if trading_type not in (TradingType.SIMULATION, TradingType.BACKTEST):
            raise Exception("Invalid trading type: {}".format(trading_type))
        self._trading_type = trading_type
        self._verbose = verbose
        self._sleep = (
            0.3
            if trading_type
            in (TradingType.LIVE, TradingType.SIMULATION, TradingType.SANDBOX)
            else 0.0
        )
        self._id = 0
        self._events: Deque[Event] = deque()
        self._pending_orders: Deque[Order] = deque()
        self._pending_cancel_orders: Deque[Order] = deque()
        SyntheticExchange._inst += 1

        self._inst_count = int(inst_count)
        self._backtest_cycles_total = int(cycles)
        self._backtest_count = 0

        self._time = datetime.now() - timedelta(days=10)

        self._omit_cancel: Set[str] = set()
        self._trend = ["buy"] * 5 + ["sell"] * 4

        self._generate_positions = positions

    def _seed(self, symbols: List[str] = None) -> None:
        self._instruments = {
            symbol: Instrument(symbol, exchange=self.exchange())
            for symbol in symbols or _getName(self._inst_count)
        }
        self._orderbooks = {
            Instrument(symbol): OrderBook(
                instrument=i, exchange_name=self._exchange, callback=lambda x: None
            )
            for symbol, i in self._instruments.items()
        }
        self._seedOrders()

    def _seedOrders(self) -> None:
        # seed all orderbooks
        for instrument, orderbook in self._orderbooks.items():

            # pick a random startpoint, endpoint, and midpoint
            offset = 50
            start = round(random() * offset, 2) + offset
            end = start + round(random() * offset + offset / 5, 2) + offset * 2
            mid = (start + end) / 2.0

            while start < end:
                side = Side.BUY if start <= mid else Side.SELL
                increment = choice((0.05, 0.1, 0.2))
                order = Order(
                    volume=round(random() * 10, 0) + 5,
                    price=start,
                    side=side,
                    instrument=instrument,
                    exchange=self._exchange,
                    order_type=OrderType.LIMIT,
                    id=self._id,
                    timestamp=self._time
                    if self._trading_type == TradingType.BACKTEST
                    else None,
                )

                orderbook.add(order)

                start = round(start + increment, 2)
                self._id += 1

    def _reseed(self, instrument: Instrument, side: Side) -> None:
        print("reseeding synthetic exchange...")
        # reseed
        orderbook = self._orderbooks[instrument]

        levels = orderbook.topOfBook()
        start = 0.1 if side == Side.BUY else levels[Side.BUY].price
        end = start + round(random() * 50 + 10, 2) + 50

        while start < end:
            increment = choice((0.1, 0.2))
            order = Order(
                volume=round(random() * 10, 0) + 20,
                price=start,
                side=side,
                instrument=instrument,
                exchange=self._exchange,
                id=self._id,
                timestamp=self._time
                if self._trading_type == TradingType.BACKTEST
                else None,
            )

            orderbook.add(order)
            start = round(start + increment, 2)

    def _jumptime(self, order: Order) -> None:
        if self._trading_type == TradingType.BACKTEST:
            order.timestamp = self._time
            self._time += timedelta(seconds=randint(25, 30))

    def __repr__(self) -> str:
        ret = ""
        for ticker, orderbook in self._orderbooks.items():
            ret += (
                "--------------------\t"
                + str(ticker)
                + "\t--------------------\n"
                + str(orderbook)
            )
        return ret

    # *************** #
    # General methods #
    # *************** #
    async def connect(self) -> None:
        """nothing to connect to"""
        self._seed()

        # set callbacks to the trading engine
        for orderbook in self._orderbooks.values():
            orderbook.setCallback(lambda event: self._events.append(event))

    async def instruments(self) -> List[Instrument]:
        """nothing to connect to"""
        return list(self._instruments.values())

    # ************ #
    # Get snapshot #
    # ************ #
    def snapshot(self) -> Iterator[Event]:
        # first return all seeded orders
        for _, orderbook in self._orderbooks.items():
            for order in orderbook:
                yield Event(type=EventType.OPEN, target=order)

    # ******************* #
    # Market Data Methods #
    # ******************* #
    async def tick(self, snapshot: bool = False) -> AsyncIterator[Event]:  # type: ignore[override]
        # first return all seeded orders if snapshot is false
        if snapshot is False:
            for _, orderbook in self._orderbooks.items():
                for order in orderbook:
                    yield Event(type=EventType.OPEN, target=order)

        # loop forever
        while True:
            if self._trading_type == TradingType.BACKTEST:
                self._backtest_count += 1
                if self._backtest_count >= self._backtest_cycles_total:
                    return

            while self._pending_cancel_orders:
                order = self._pending_cancel_orders.popleft()
                self._jumptime(order)

                try:
                    self._orderbooks[order.instrument].cancel(order)
                except KeyboardInterrupt:
                    raise
                except BaseException:
                    continue

                yield Event(EventType.CANCEL, order)
                await asyncio.sleep(self._sleep)

            while self._pending_orders:
                order = self._pending_orders.popleft()
                self._jumptime(order)
                self._orderbooks[order.instrument].add(order)
                await asyncio.sleep(self._sleep)

            while self._events:
                event = self._events.popleft()
                yield event
                # await asyncio.sleep(self._sleep)

            await asyncio.sleep(self._sleep)

            # choose a random symbol
            symbol = choice(list(self._instruments.keys()))
            instrument = self._instruments[symbol]
            orderbook = self._orderbooks[instrument]

            # add a new buy order, a new sell order, or a cross
            do = choice(["buy", "sell"] + ["change"] * 5 + ["cross"] + ["cancel"] * 2)
            levels = orderbook.topOfBook()
            volume = round(random() * 10, 0) + 10

            if do == "buy":
                # new buy order
                # choose a price level
                price = round(levels[Side.BUY].price - choice((0, 0.5, 1, 1.5, 2)), 2)
                order = Order(
                    volume=volume,
                    price=price,
                    side=Side.BUY,
                    instrument=instrument,
                    exchange=self._exchange,
                    order_type=OrderType.LIMIT,
                    id=self._id,
                )

                self._jumptime(order)  # advance time in backtest

                orderbook.add(order)
                self._id += 1

            elif do == "sell":
                # new sell order
                price = round(levels[Side.SELL].price + choice((0, 0.5, 1, 1.5, 2)), 2)

                if price == float("inf"):
                    # liquidity exausted
                    self._reseed(instrument, Side.SELL)
                    continue

                order = Order(
                    volume=volume,
                    price=price,
                    side=Side.SELL,
                    instrument=instrument,
                    exchange=self._exchange,
                    order_type=OrderType.LIMIT,
                    id=self._id,
                )

                self._jumptime(order)  # advance time in backtest

                orderbook.add(order)
                self._id += 1

            elif do == "cross":
                # cross the spread

                # update trends
                if random() < 0.1:
                    self._trend.append("sell")
                # if random() < .2:
                #     self._trend = [{'buy': 'sell', 'sell': 'buy'}.get(_) for _ in self._trend]
                elif random() > 0.9:
                    # accelerate the trend
                    self._trend.append("buy")

                side = choice(self._trend)
                if side == "buy":
                    # cross to buy
                    price = round(levels[Side.BUY].price + choice((1, 2, 5)), 2)

                    if price <= 0.0:
                        # liquidity exausted
                        self._reseed(instrument, Side.BUY)
                        continue

                    order = Order(
                        volume=volume,
                        price=price,
                        side=Side.BUY,
                        instrument=instrument,
                        exchange=self._exchange,
                        order_type=OrderType.LIMIT,
                        id=self._id,
                    )

                    self._jumptime(order)  # advance time in backtest

                    orderbook.add(order)
                    self._id += 1

                else:
                    # cross to sell
                    price = round(levels[Side.SELL].price - choice((1, 2, 5)), 2)

                    if price == float("inf"):
                        # liquidity exausted
                        self._reseed(instrument, Side.SELL)
                        continue

                    order = Order(
                        volume=volume,
                        price=price,
                        side=Side.SELL,
                        instrument=instrument,
                        exchange=self._exchange,
                        order_type=OrderType.LIMIT,
                        id=self._id,
                    )

                    self._jumptime(order)  # advance time in backtest

                    orderbook.add(order)
                    self._id += 1

            elif do == "cancel" or do == "change":
                # cancel an existing order
                side = choice(("buy", "sell"))
                levels2 = orderbook.levels(5)
                if side == "buy" and levels2:
                    level = choice(levels2[Side.BUY])
                    price_level = orderbook.level(price=level.price)[1]
                    if price_level is None:
                        continue

                    orders = price_level._orders
                    if orders:
                        order = choice(orders)

                        if order.id in self._omit_cancel:
                            continue

                        self._jumptime(order)  # advance time in backtest

                        if do == "cancel":
                            orderbook.cancel(order)

                        else:
                            new_volume = max(order.volume + choice((-5, -1, 1, 5)), 1.0)
                            if new_volume > order.filled:
                                order.volume = new_volume
                                orderbook.change(order)
                            else:
                                orderbook.cancel(order)

                elif levels2:
                    level = choice(levels2[Side.SELL])
                    price_level = orderbook.level(price=level.price)[0]
                    if price_level is None:
                        continue

                    orders = price_level._orders
                    if orders:
                        self._jumptime(order)  # advance time in backtest
                        order = choice(orders)

                        if order.id in self._omit_cancel:
                            continue

                        if do == "cancel":
                            orderbook.cancel(order)

                        else:
                            new_volume = max(order.volume + choice((-5, -1, 1, 5)), 1.0)
                            if new_volume > order.filled:
                                order.volume = new_volume
                                orderbook.change(order)
                            else:
                                orderbook.cancel(order)

            # print current state if running in verbose mode
            if self._verbose:
                print(self)

    # ******************* #
    # Order Entry Methods #
    # ******************* #
    async def newOrder(self, order: Order) -> bool:
        if order.instrument not in self._instruments.values():
            # invalid instrument
            return False

        # assign id
        order.id = str(self._id)

        # adjust time if backtesting

        self._jumptime(order)
        # fix exchange if messed up
        # if order.exchange != self.exchange():
        #     order.exchange = self.exchange()

        self._id += 1
        self._pending_orders.append(order)
        self._omit_cancel.add(order.id)  # don't cancel user orders
        return True

    async def cancelOrder(self, order: Order) -> bool:
        self._pending_cancel_orders.append(order)
        return True

    async def accounts(self) -> List[Position]:
        if self._generate_positions:
            ret = []

            for instrument in self._instruments.values():
                pos = Position(
                    randint(0, 10),
                    self._orderbooks[instrument].topOfBook()[Side.BUY].price,
                    self._time,
                    instrument,
                    self.exchange(),
                    [],
                )
                ret.append(pos)
            return ret
        return []
