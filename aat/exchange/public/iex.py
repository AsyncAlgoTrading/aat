import asyncio
import pandas as pd  # type: ignore
import pyEX  # type: ignore
from collections import deque
from datetime import datetime, timedelta
from tqdm import tqdm
from aat.exchange import Exchange
from aat.config import InstrumentType, EventType, Side, TradingType
from aat.core import ExchangeType, Instrument, Event, Trade, Order

_iex_instrument_types = {
    'ad': InstrumentType.EQUITY,  # ad - ADR
    'gdr': InstrumentType.EQUITY,  # gdr - GDR
    're': InstrumentType.OTHER,  # re - REIT
    'ce': InstrumentType.MUTUALFUND,  # ce - Closed end fund
    'si': InstrumentType.EQUITY,  # si - Secondary Issue
    'lp': InstrumentType.OTHER,  # lp - Limited Partnerships
    'cs': InstrumentType.EQUITY,  # cs - Common Stock
    'et': InstrumentType.EQUITY,  # et - ETF
    'wt': InstrumentType.OTHER,  # wt - Warrant
    'rt': InstrumentType.OTHER,  # rt – Right
    'oef': InstrumentType.MUTUALFUND,  # oef - Open Ended Fund
    'cef': InstrumentType.MUTUALFUND,  # cef - Closed Ended Fund
    'ps': InstrumentType.EQUITY,  # ps - Preferred Stock
    'ut': InstrumentType.OTHER,  # ut - Unit
    'struct': InstrumentType.OTHER,  # struct - Structured Product
}


class IEX(Exchange):
    '''Investor's Exchange'''

    def __init__(self, trading_type, verbose, api_key, is_sandbox, timeframe='1y', start_date=None, end_date=None):
        super().__init__(ExchangeType('iex'))
        self._trading_type = trading_type
        self._verbose = verbose
        self._api_key = api_key
        self._is_sandbox = is_sandbox

        if trading_type == TradingType.LIVE:
            assert not is_sandbox

        self._timeframe = timeframe

        if timeframe == 'live':
            assert trading_type != TradingType.BACKTEST

        if timeframe == '1d':
            # intraday testing
            # TODO if today is weekend/holiday, pick last day with data
            self._start_date = datetime.strptime(start_date, '%Y%m%d') if start_date else datetime.today()
            self._end_date = datetime.strptime(end_date, '%Y%m%d') if end_date else datetime.today()

        self._subscriptions = []

        # "Order" management
        self._queued_orders = deque()
        self._order_id = 1

    # *************** #
    # General methods #
    # *************** #
    async def connect(self):
        '''connect to exchange. should be asynchronous.

        For OrderEntry-only, can just return None
        '''
        self._client = pyEX.Client(self._api_key, 'sandbox' if self._is_sandbox else 'stable')

    # ******************* #
    # Market Data Methods #
    # ******************* #
    async def instruments(self):
        '''get list of available instruments'''
        instruments = []
        symbols = self._client.symbols()
        for record in symbols:
            if not record['isEnabled'] or not record['type']:
                continue
            symbol = record['symbol']
            brokerExchange = record['exchange']
            type = _iex_instrument_types[record['type']]
            currency = Instrument(type=InstrumentType.CURRENCY, name=record['currency'])

            try:
                inst = Instrument(name=symbol, type=type, exchange=self.exchange(), brokerExchange=brokerExchange, currency=currency)
            except AssertionError:
                # Happens sometimes on sandbox
                continue
            instruments.append(inst)
        return instruments

    def subscribe(self, instrument):
        self._subscriptions.append(instrument)

    async def tick(self):
        '''return data from exchange'''

        if self._timeframe == 'live':
            raise NotImplementedError()

        else:
            dfs = []
            if self._timeframe != '1d':
                for i in tqdm(self._subscriptions, desc="Fetching data..."):
                    df = self._client.chartDF(i.name, timeframe=self._timeframe)
                    df = df[['close', 'volume']]
                    df.columns = ['close:{}'.format(i.name), 'volume:{}'.format(i.name)]
                    dfs.append(df)
                data = pd.concat(dfs, axis=1)
                data.sort_index(inplace=True)
                data = data.groupby(data.index).last()
                data.drop_duplicates(inplace=True)
                data.fillna(method='ffill', inplace=True)
            else:
                for i in tqdm(self._subscriptions, desc="Fetching data..."):
                    date = self._start_date
                    subdfs = []
                    while date <= self._end_date:
                        df = self._client.chartDF(i.name, timeframe='1d', date=date.strftime('%Y%m%d'))
                        if not df.empty:
                            df = df[['average', 'volume']]
                            df.columns = ['close:{}'.format(i.name), 'volume:{}'.format(i.name)]
                            subdfs.append(df)
                        date += timedelta(days=1)
                    dfs.append(pd.concat(subdfs))

                data = pd.concat(dfs, axis=1)
                data.index = [x + timedelta(hours=int(y.split(':')[0]), minutes=int(y.split(':')[1])) for x, y in data.index]
                data = data.groupby(data.index).last()
                data.drop_duplicates(inplace=True)
                data.fillna(method='ffill', inplace=True)

            for index in data.index:
                for i in self._subscriptions:
                    volume = data.loc[index]['volume:{}'.format(i.name)]
                    price = data.loc[index]['close:{}'.format(i.name)]
                    if volume == 0:
                        continue

                    o = Order(volume=volume, price=price, side=Side.BUY, instrument=i, exchange=self.exchange())
                    o.timestamp = index.to_pydatetime()

                    t = Trade(volume=volume, price=price, taker_order=o, maker_orders=[])

                    yield Event(type=EventType.TRADE, target=t)
                    await asyncio.sleep(0)

                while self._queued_orders:
                    order = self._queued_orders.popleft()
                    order.timestamp = index

                    t = Trade(volume=order.volume, price=order.price, taker_order=order, maker_orders=[])
                    t.my_order = order

                    yield Event(type=EventType.TRADE, target=t)
                    await asyncio.sleep(0)

    # ******************* #
    # Order Entry Methods #
    # ******************* #
    async def newOrder(self, order: Order):
        '''submit a new order to the exchange. should set the given order's `id` field to exchange-assigned id

        For MarketData-only, can just return None
        '''
        if self._trading_type == TradingType.LIVE:
            raise NotImplementedError("Live OE not available for IEX")

        order.id = self._order_id
        self._order_id += 1
        self._queued_orders.append(order)
        return order

    # Not implemented, data-only


Exchange.registerExchange('iex', IEX)
