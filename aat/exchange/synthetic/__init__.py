import asyncio
import numpy as np  # type: ignore
import string
from collections import deque
from random import choice, random
from ..exchange import Exchange
from ...core import Instrument, OrderBook, Order, Event, ExchangeType
from ...config import Side, EventType


def _getName(n=1):
    columns = [''.join(np.random.choice(list(string.ascii_uppercase), choice((1, 2, 3, 4)))) + '.' + ''.join(np.random.choice(list(string.ascii_uppercase), choice((1, 2)))) for _ in range(n)]
    return columns


class SyntheticExchange(Exchange):
    _inst = 0

    def __init__(self, trading_type=None, verbose=False, **kwargs):
        super().__init__(ExchangeType('synthetic{}'.format(SyntheticExchange._inst)))
        self._trading_type = trading_type
        self._verbose = verbose
        self._sleep = 0.1 if trading_type in ("live", "simulation") else 0.0
        self._id = 0
        self._events = deque()
        self._pending_orders = deque()
        SyntheticExchange._inst += 1

        self._backtest_count = 0

    def _seed(self, symbols=None):
        self._instruments = {symbol: Instrument(symbol) for symbol in symbols or _getName(1)}
        self._orderbooks = {Instrument(symbol): OrderBook(instrument=i, exchange_name=self._exchange, callback=lambda x: None) for symbol, i in self._instruments.items()}
        self._seedOrders()

    def _seedOrders(self):
        # seed all orderbooks
        for instrument, orderbook in self._orderbooks.items():

            # pick a random startpoint, endpoint, and midpoint
            start = round(random() * 50, 2) + 50
            end = start + round(random() * 50 + 10, 2) + 50
            mid = (start + end) / 2.0

            while start < end:
                side = Side.BUY if start <= mid else Side.SELL
                increment = choice((.01, .05, .1, .2))
                order = Order(volume=round(random() * 10, 0) + 1,
                              price=start,
                              side=side,
                              instrument=instrument,
                              exchange=self._exchange)
                order.id = self._id

                orderbook.add(order)

                start = round(start + increment, 2)
                self._id += 1

    def __repr__(self):
        ret = ''
        for ticker, orderbook in self._orderbooks.items():
            ret += '--------------------\t' + str(ticker) + '\t--------------------\n' + str(orderbook)
        return ret

    async def connect(self):
        '''nothing to connect to'''
        self._seed()

        # set callbacks to the trading engine
        for orderbook in self._orderbooks.values():
            orderbook.setCallback(lambda event: self._events.append(event))

    async def tick(self):

        # first return all seeded orders
        for _, orderbook in self._orderbooks.items():
            for order in orderbook:
                yield Event(type=EventType.OPEN, target=order)

        # loop forever
        while True:
            if self._trading_type == 'backtest':
                self._backtest_count += 1
                if self._backtest_count >= 10000:
                    return

            while self._pending_orders:
                order = self._pending_orders.popleft()
                self._orderbooks[order.instrument].add(order)
                await asyncio.sleep(self._sleep)

            while self._events:
                event = self._events.popleft()
                yield event
                await asyncio.sleep(self._sleep)
            await asyncio.sleep(self._sleep)
            # choose a random symbol
            symbol = choice(list(self._instruments.keys()))
            instrument = self._instruments[symbol]
            orderbook = self._orderbooks[instrument]

            # add a new buy order, a new sell order, or a cross
            do = choice(['buy', 'sell', 'change'] * 20 + ['cross'] + ['cancel'] * 10)
            levels = orderbook.topOfBook()
            volume = round(random() * 5, 0) + 1

            if do == 'buy':
                # new buy order
                # choose a price level
                price = round(levels[Side.SELL][0] - choice((.01, .05, .1, .2)), 2)
                order = Order(volume=volume,
                              price=price,
                              side=Side.BUY,
                              instrument=instrument,
                              exchange=self._exchange)
                order.id = self._id
                orderbook.add(order)
                self._id += 1
            elif do == 'sell':
                # new sell order
                price = round(levels[Side.BUY][0] - choice((.01, .05, .1, .2)), 2)
                order = Order(volume=volume,
                              price=price,
                              side=Side.SELL,
                              instrument=instrument,
                              exchange=self._exchange)
                order.id = self._id
                orderbook.add(order)
                self._id += 1
            elif do == 'cross':
                # cross the spread
                side = choice(('buy', 'sell'))
                volume = volume * 2
                if side == 'buy':
                    # cross to buy
                    price = round(levels[Side.SELL][0] + choice((0.0, .01, .05)), 2)
                    order = Order(volume=volume,
                                  price=price,
                                  side=Side.BUY,
                                  instrument=instrument,
                                  exchange=self._exchange)
                    order.id = self._id
                    orderbook.add(order)
                    self._id += 1
                else:
                    # cross to sell
                    price = round(levels[Side.BUY][0] - choice((0.0, .01, .05)), 2)
                    order = Order(volume=volume,
                                  price=price,
                                  side=Side.BUY,
                                  instrument=instrument,
                                  exchange=self._exchange)
                    order.id = self._id
                    orderbook.add(order)
                    self._id += 1

            elif do == 'cancel' or do == 'change':
                # cancel an existing order
                side = choice(('buy', 'sell'))
                levels = orderbook.levels(5)
                if side == 'buy' and levels:
                    level = choice(levels[Side.BUY])
                    price_level = orderbook.level(price=level[0])[1]
                    if price_level is None:
                        continue

                    orders = price_level._orders
                    if orders:
                        order = choice(orders)

                        if do == 'cancel':
                            orderbook.cancel(order)
                        else:
                            new_volume = max(order.volume + choice((-1, -.5, .5, 1)), 1.0)
                            if new_volume > order.filled:
                                order.volume = new_volume
                                orderbook.change(order)
                            else:
                                orderbook.cancel(order)

                elif levels:
                    level = choice(levels[Side.SELL])
                    price_level = orderbook.level(price=level[0])[0]
                    if price_level is None:
                        continue

                    orders = price_level._orders
                    if orders:
                        order = choice(orders)
                        if do == 'cancel':
                            orderbook.cancel(order)
                        else:
                            new_volume = max(order.volume + choice((-1, -.5, .5, 1)), 1.0)
                            if new_volume > order.filled:
                                order.volume = new_volume
                                orderbook.change(order)
                            else:
                                orderbook.cancel(order)

            # print current state if running in verbose mode
            if self._verbose:
                print(self)

    async def newOrder(self, order: Order):
        order.id = self._id
        self._id += 1
        self._pending_orders.append(order)
        return order


Exchange.registerExchange('synthetic', SyntheticExchange)
