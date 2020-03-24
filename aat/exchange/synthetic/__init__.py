import numpy as np
import string
from random import choice
from ..exchange import Exchange
from ...core import Instrument, OrderBook


def _getName(n=1):
    columns = [''.join(np.random.choice(list(string.ascii_uppercase), choice((1, 2, 3, 4)))) + '.' + ''.join(np.random.choice(list(string.ascii_uppercase), choice((1, 2)))) for _ in range(n)]
    return columns


class SyntheticExchange(Exchange):
    def __init__(self, trading_engine=None):
        pass

    def _seed(self, symbols=None):
        self._instruments = {symbol: Instrument(symbol) for symbol in symbols or _getName(10)}
        self._orderbooks = {symbol: OrderBook(i) for symbol, i in self._instruments.items()}
        print(self._instruments)

    async def connect(self):
        return

    async def tick(self):
        yield 'test'
        yield 'test2'



Exchange.registerExchange('synthetic', SyntheticExchange)
