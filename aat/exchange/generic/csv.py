import csv
from collections import deque
from typing import List
from aat.config import EventType, InstrumentType, Side, TradingType
from aat.core import ExchangeType, Event, Instrument, Trade, Order
from aat.exchange import Exchange


class CSV(Exchange):
    '''CSV File Exchange'''

    def __init__(self, trading_type, verbose, filename: str):
        super().__init__(ExchangeType('csv-{}'.format(filename)))
        self._trading_type = trading_type
        self._verbose = verbose
        self._filename = filename
        self._data: List[Trade] = []
        self._queued_orders = deque()
        self._order_id = 1

    async def instruments(self):
        '''get list of available instruments'''
        return list(set(_.instrument for _ in self._data))

    async def connect(self):
        with open(self._filename) as csvfile:
            self._reader = csv.DictReader(csvfile, delimiter=',')

            for row in self._reader:
                self._data.append(Trade(volume=float(row['volume']),
                                        price=float(row['close']),
                                        maker_orders=[],
                                        taker_order=Order(volume=float(row['volume']),
                                                          price=float(row['close']),
                                                          side=Side.BUY,
                                                          exchange=self.exchange(),
                                                          instrument=Instrument(
                                                              row['symbol'].split('-')[0],
                                                              InstrumentType(row['symbol'].split('-')[1].upper())
                                        )
                )
                ))

    async def tick(self):
        for item in self._data:
            yield Event(EventType.TRADE, item)

    async def newOrder(self, order: Order):
        if self._trading_type == TradingType.LIVE:
            raise NotImplementedError("Live OE not available for CSV")

        order.id = self._order_id
        self._order_id += 1
        self._queued_orders.append(order)
        return order


class CSV2(Exchange):
    '''CSV File Exchange'''

    def __init__(self, trading_type, verbose, filename: str, value_field=''):
        super().__init__(ExchangeType('csv-{}'.format(filename)))
        self._trading_type = trading_type
        self._verbose = verbose
        self._filename = filename
        self._data: List[Trade] = []
        self._value_field = value_field

    async def instruments(self):
        '''get list of available instruments'''
        return list(set(_.instrument for _ in self._data))

    async def connect(self):
        with open(self._filename) as csvfile:
            self._reader = csv.DictReader(csvfile, delimiter=',')

            for row in self._reader:
                if self._value_field:
                    value = row[self._value_field]
                if 'value' in row:
                    value = row['value']
                elif 'price' in row:
                    value = row['price']
                elif 'close' in row:
                    # OHLC data
                    value = row['close']
                else:
                    raise Exception('Must provide a value field or "value", "price", "close"')

                _ = value
                # TODO make this smarter or more configureable


Exchange.registerExchange('csv', CSV)
