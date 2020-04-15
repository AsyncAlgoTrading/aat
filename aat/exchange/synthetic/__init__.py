import asyncio
import numpy as np  # type: ignore
import string
from collections import deque
from datetime import datetime
from random import choice, random
from ..exchange import Exchange
from ...core import Instrument, OrderBook, Order, Event, ExchangeType
from ...config import Side, DataType, EventType


def _getName(n=1):
    columns = [''.join(np.random.choice(list(string.ascii_uppercase), choice((1, 2, 3, 4)))) + '.' + ''.join(np.random.choice(list(string.ascii_uppercase), choice((1, 2)))) for _ in range(n)]
    return columns


class SyntheticExchange(Exchange):
    _inst = 0

    def __init__(self, verbose=False, **kwargs):
        super().__init__(ExchangeType('synthetic{}'.format(SyntheticExchange._inst)))
        self._verbose = verbose
        self._id = 0
        self._events = deque()
        self._pending_orders = deque()
        SyntheticExchange._inst += 1

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
                orderbook.add(Order(id=self._id,
                                    timestamp=datetime.now().timestamp(),
                                    volume=round(random() * 10, 0),
                                    price=start,
                                    side=side,
                                    type=DataType.ORDER,
                                    instrument=instrument,
                                    exchange=self._exchange))
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
            orderbook.setCallback(self._events.append)

    async def tick(self):

        # first return all seeded orders
        for _, orderbook in self._orderbooks.items():
            for order in orderbook:
                yield Event(type=EventType.OPEN, target=order)

        # loop forever
        while True:
            while self._pending_orders:
                order = self._pending_orders.popleft()
                self._orderbooks[order.instrument].add(order)
                await asyncio.sleep(.1)

            while self._events:
                event = self._events.popleft()
                yield event
                await asyncio.sleep(.1)
            await asyncio.sleep(.1)
            # choose a random symbol
            symbol = choice(list(self._instruments.keys()))
            instrument = self._instruments[symbol]
            orderbook = self._orderbooks[instrument]

            # add a new buy order, a new sell order, or a cross
            do = choice(('buy', 'sell', 'cross', 'cancel', 'change'))
            levels = orderbook.topOfBook()
            volume = round(random() * 5, 0)

            if do == 'buy':
                # new buy order
                # choose a price level
                price = round(levels['ask'][0] - choice((.01, .05, .1, .2)), 2)
                orderbook.add(Order(id=self._id,
                                    timestamp=datetime.now().timestamp(),
                                    volume=volume,
                                    price=price,
                                    side=Side.BUY,
                                    type=DataType.ORDER,
                                    instrument=instrument,
                                    exchange=self._exchange))
                self._id += 1
            elif do == 'sell':
                # new sell order
                price = round(levels['bid'][0] - choice((.01, .05, .1, .2)), 2)
                orderbook.add(Order(id=self._id,
                                    timestamp=datetime.now().timestamp(),
                                    volume=volume,
                                    price=price,
                                    side=Side.SELL,
                                    type=DataType.ORDER,
                                    instrument=instrument,
                                    exchange=self._exchange))
                self._id += 1
            elif do == 'cross':
                # cross the spread
                side = choice(('buy', 'sell'))
                if side == 'buy':
                    # cross to buy
                    price = round(levels['ask'][0] + choice((0.0, .01, .05)), 2)
                    orderbook.add(Order(id=self._id,
                                        timestamp=datetime.now().timestamp(),
                                        volume=volume,
                                        price=price,
                                        side=Side.BUY,
                                        type=DataType.ORDER,
                                        instrument=instrument,
                                        exchange=self._exchange))
                    self._id += 1
                else:
                    # cross to sell
                    price = round(levels['bid'][0] - choice((0.0, .01, .05)), 2)
                    orderbook.add(Order(id=self._id,
                                        timestamp=datetime.now().timestamp(),
                                        volume=volume,
                                        price=price,
                                        side=Side.SELL,
                                        type=DataType.ORDER,
                                        instrument=instrument,
                                        exchange=self._exchange))
                    self._id += 1
            elif do == 'cancel' or do == 'change':
                # cancel an existing order
                side = choice(('buy', 'sell'))
                levels = orderbook.levels(5)
                if side == 'buy' and levels:
                    level = choice(levels['bid'])
                    price_level = orderbook.level(price=level[0])[1]
                    if price_level is None:
                        continue

                    orders = price_level._orders
                    if orders:
                        order = choice(orders)

                        if do == 'cancel':
                            orderbook.cancel(order)
                        else:
                            order.volume = max(order.volume + choice((-1, -.5, .5, 1)), 1.0)
                            orderbook.add(order)

                elif levels:
                    level = choice(levels['ask'])
                    orders = orderbook.level(price=level[0])[0]._orders
                    if orders:
                        order = choice(orders)
                        if do == 'cancel':
                            orderbook.cancel(order)
                        else:
                            order.volume = max(order.volume + choice((-1, -.5, .5, 1)), 1.0)
                            orderbook.add(order)

            # print current state if running in verbose mode
            if self._verbose:
                print(self)

    def newOrder(self, order: Order):
        self._pending_orders.append(order)


Exchange.registerExchange('synthetic', SyntheticExchange)
