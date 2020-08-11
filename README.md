
<img src="https://raw.githubusercontent.com/AsyncAlgoTrading/aat/master/docs/img/icon.png" width="200px"></img>

[![Build Status](https://dev.azure.com/tpaine154/aat/_apis/build/status/AsyncAlgoTrading.aat?branchName=master)](https://dev.azure.com/tpaine154/aat/_build/latest?definitionId=19&branchName=master)
[![Coverage](https://img.shields.io/azure-devops/coverage/tpaine154/aat/19/master)](https://dev.azure.com/tpaine154/aat/_apis/build/status/AsyncAlgoTrading.aat?branchName=master)
[![License](https://img.shields.io/github/license/timkpaine/aat.svg)](https://pypi.python.org/pypi/aat)
[![PyPI](https://img.shields.io/pypi/v/aat.svg)](https://pypi.python.org/pypi/aat)
[![Docs](https://img.shields.io/readthedocs/aat.svg)](http://aat.readthedocs.io/en/latest/)
 
`aat` is an asynchronous, event-driven framework for writing algorithmic trading strategies in python with optional acceleration in C++. It is designed to be modular and extensible, with support for a wide variety of instruments and strategies, live trading across (and between) multiple exchanges, fully integrated backtesting support, slippage and transaction cost modeling, and robust reporting and risk mitigation through manual and programatic algorithm controls.

Like [Zipline](https://github.com/quantopian/zipline) and [Lean](https://github.com/QuantConnect/Lean), `aat` exposes a single strategy class which is utilized for both live trading and backtesting. The strategy class is simple enough to write and test algorithms quickly, but extensible enough to allow for complex slippage and transaction cost modeling, as well as mid- and post- trade analysis.  


# Overview
## Internals
`aat`'s engine is composed of 4 major parts. 

- trading engine
- risk management engine
- execution engine
- backtest engine

### Trading Engine
The trading engine initializes all exchanges and strategies, then martials data, trade requests, and trade responses between the strategy, risk, execution, and exchange objects, while keeping track of high-level statistics on the system

### Risk Management Engine
The risk management engine enforces trading limits, making sure that stategies are limited to certain risk profiles. It can modify or remove trade requests prior to execution depending on user preferences and outstanding positions and orders.

### Execution engine
The execution engine is a simple passthrough to the underlying exchanges. It provides a unified interface for creating various types of orders.

### Backtest engine
The backtest engine provides the ability to run the same stragegy offline against historical data.

## Core Components
`aat` has a variety of core classes and data structures, the most important of which are the `Strategy` and `Exchange` classes.

### Trading Strategy
The core element of `aat` is the trading strategy interface. It includes both data processing and order management functionality. Users subclass this class in order to implement their strategies. Methods of the form `onNoun` are used to handle market data events, while methods of the form `onVerb` are used to handle order entry events. There are also a variety of order management and data subscription methods available.

The only method that is required to be implemented is the `onTrade` method. The full specification of a strategy is given here (we will look at an example below).



```python3
class Strategy(metaclass=ABCMeta):
    #########################
    # Event Handler Methods #
    #########################
    @abstractmethod
    async def onTrade(self, event: Event):
        '''Called whenever a `Trade` event is received'''

    async def onOrder(self, event: Event) -> None:
        '''Called whenever an Order `Open`, `Cancel`, `Change`, or `Fill` event is received'''
        pass

    async def onOpen(self, event: Event):
        '''Called whenever an Order `Open` event is received'''

    async def onFill(self, event: Event):
        '''Called whenever an Order `Fill` event is received'''

    async def onCancel(self, event: Event):
        '''Called whenever an Order `Cancel` event is received'''

    async def onChange(self, event: Event):
        '''Called whenever an Order `Change` event is received'''

    async def onError(self, event: Event):
        '''Called whenever an internal error occurs'''

    async def onStart(self):
        '''Called once at engine initialization time'''

    async def onExit(self):
        '''Called once at engine exit time'''

    async def onHalt(self, data):
        '''Called whenever an exchange `Halt` event is received, i.e. an event to stop trading'''

    async def onContinue(self, data):
        '''Called whenever an exchange `Continue` event is received, i.e. an event to continue trading'''

    #########################
    # Order Entry Callbacks #
    #########################
    async def onBought(self, event: Event):
        '''Called on my order bought'''
        pass

    async def onSold(self, event: Event):
        '''Called on my order sold'''
        pass

    async def onTraded(self, event: Event):
        '''Called on my order bought or sold'''
        pass

    async def onRejected(self, event: Event):
        '''Called on my order rejected'''
        pass

    async def onCanceled(self, event: Event):
        '''Called on my order canceled'''
        pass

    #######################
    # Order Entry Methods #
    #######################
    async def newOrder(self, order: Order):
        '''helper method, defers to buy/sell'''

    async def cancelOrder(self, order: Order):
        '''cancel an open order'''

    async def buy(self, order: Order):
        '''submit a buy order. Note that this is merely a request for an order, it provides no guarantees that the order will
        execute. At a later point, if your order executes, you will receive an alert via the `bought` method'''

    async def sell(self, order: Order):
        '''submit a sell order. Note that this is merely a request for an order, it provides no guarantees that the order will
        execute. At a later point, if your order executes, you will receive an alert via the `sold` method'''

    def orders(self, instrument: Instrument = None, exchange: ExchangeType = None, side: Side = None):
        '''select all open orders'''

    def pastOrders(self, instrument: Instrument = None, exchange: ExchangeType = None, side: Side = None):
        '''select all past orders'''

    def trades(self, instrument: Instrument = None, exchange: ExchangeType = None, side: Side = None):
        '''select all past trades'''

    def accounts(self) -> List:
        '''get accounts from source'''

    ################
    # Risk Methods #
    ################
    def positions(self, instrument: Instrument = None, exchange: ExchangeType = None, side: Side = None):
        '''select all positions'''

    def risk(self, position=None):
        '''Get risk metrics'''

    def priceHistory(self, instrument: Instrument):
        '''Get price history for an asset'''

    #################
    # Other Methods #
    #################
    def now(self):
        '''Return the current datetime. Useful to avoid code changes between
        live trading and backtesting. Defaults to `datetime.now`'''

    def instruments(self, type=None, exchange=None):
        '''Return list of all available instruments'''

    def exchanges(self, instrument_type=None):
        '''Return list of all available exchanges'''

    def subscribe(self, instrument=None):
        '''Subscribe to market data for the given instrument'''

    def lookup(self, instrument):
        '''lookup an instrument on the exchange'''
```

### Example Strategy
Here is a simple trading strategy that buys once and holds. 

```python3
from aat import Strategy, Event, Order, Trade, Side

class BuyAndHoldStrategy(Strategy):
    def __init__(self, *args, **kwargs) -> None:
        super(BuyAndHoldStrategy, self).__init__(*args, **kwargs)

    async def onTrade(self, event: Event) -> None:
        '''Called whenever a `Trade` event is received'''
        trade: Trade = event.target

        # no past trades, no current orders
        if not self.orders(trade.instrument) and not self.trades(trade.instrument):
            req = Order(side=Side.BUY,
                        price=trade.price,
                        volume=1,
                        instrument=trade.instrument,
                        order_type=Order.Types.MARKET,
                        exchange=trade.exchange)

            print("requesting buy : {}".format(req))
            await self.newOrder(req)

    async def onBought(self, event: Event) -> None:
        trade: Trade = event.target
        print('bought {:.2f} @ {:.2f}'.format(trade.volume, trade.price))

    async def onRejected(self, event: Event) -> None:
        print('order rejected')
        import sys
        sys.exit(0)

    async def onExit(self, event: Event) -> None:
        print('Finishing...')

```

Trading strategies have only one required method handling messages:

- onTrade: Called when a trade occurs

There are other optional callbacks for more granular processing:

- onOrder: Called whenever a new order occurs, an order is filled, an order is cancelled, or an order is modified (includes the behavior of onOpen, onFill, onCancel, and onChange)
- onOpen: Called when a new order occurs
- onFill: Called when an order is filled
- onCancel: Called when an order is cancelled
- onChange: Called when an order is modified
- onError: Called when a system error occurs
- onHalt: Called when trading is halted
- onContinue: Called when trading continues
- onStart: Called when the program starts
- onExit: Called when the program shuts down

There are several callbacks for order entry:
- onTraded: called when a strategy's order is bought or sold
- onBought: called when a strategy's order is bought
- onSold: called when a strategy's order is sold
- onRejected: called when a strategy's order is rejected
- onCanceled: called when a strategy's order is canceled

There are several methods for order entry and data subscriptions:

- subscribe: subscribe to an instrument/exchange data
- instruments: get available instruments
- exchanges: get available exchanges
- newOrder: submit a new order
- buy  (alias of newOrder): submit a new order
- sell (alias of newOrder): submit a new order
- orders: get open orders
- pastOrders: get past orders
- trades: get past trades
- positions: get position informatino
- risk: get risk information
- now: get current time as of engine (`datetime.now` when running in realtime)

There are also several optional callbacks for backtesting:

- slippage
- transactionCost

### Exchanges
An exchange instance inherits from two base class, a `MarketData` class which implements data streaming methods, and an `OrderEntry` class which implements order entry methods.


#### Market Data Class
```python3
class _MarketData(metaclass=ABCMeta):
    '''internal only class to represent the streaming-source
    side of a data source'''

    async def instruments(self):
        '''get list of available instruments'''

    def subscribe(self, instrument):
        '''subscribe to market data for a given instrument'''

    async def tick(self):
        '''return data from exchange'''
```

#### Order Entry Class
```python3
class _OrderEntry(metaclass=ABCMeta):
    '''internal only class to represent the rest-sink
    side of a data source'''

    def accounts(self) -> List:
        '''get accounts from source'''

    async def newOrder(self, order: Order):
        '''submit a new order to the exchange. should set the given order's `id` field to exchange-assigned id

        For MarketData-only, can just return None
        '''

    async def cancelOrder(self, order: Order):
        '''cancel a previously submitted order to the exchange.

        For MarketData-only, can just return None
        '''
```

#### Exchange Class
```python3
class Exchange(_MarketData, _OrderEntry):
    '''Generic representation of an exchange. There are two primary functionalities of an exchange.

    Market Data Source:
        exchanges can stream data to the engine

    Order Entry Sink:
        exchanges can be queried for data, or send data
    '''
    @abstractmethod
    async def connect(self):
        '''connect to exchange. should be asynchronous.

        For OrderEntry-only, can just return None
        '''
```

#### Extending
Writing a custom exchange is very easy, you just need to implement the market data interface, the order entry interface, or both. Here is a simple example of implementing a market data exchange on top of IEX Cloud, with support for simulated order entry by accepting any trade submitted at the price asked for:

```python3
class IEX(Exchange):
    '''Investor's Exchange'''

    def __init__(self, trading_type, verbose, api_key, is_sandbox):
        super().__init__(ExchangeType('iex'))
        self._trading_type = trading_type
        self._verbose = verbose
        self._api_key = api_key
        self._is_sandbox = is_sandbox
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
        self._client = pyEX.Client(self._api_key, 'sandbox' if self._is_sandbox else 'v1')

    # ******************* #
    # Market Data Methods #
    # ******************* #
    async def instruments(self):
        '''get list of available instruments'''
        instruments = []
        symbols = self._client.symbols()
        for record in symbols:
            if not record['isEnabled']:
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
        dfs = []
        for i in self._subscriptions:
            df = self._client.chartDF(i.name, timeframe='6m')
            df = df[['close', 'volume']]
            df.columns = ['close:{}'.format(i.name), 'volume:{}'.format(i.name)]
            dfs.append(df)

        data = pd.concat(dfs, axis=1)
        data.sort_index(inplace=True)
        data = data.groupby(data.index).last()
        data.drop_duplicates(inplace=True)
        data.fillna(method='ffill', inplace=True)

        for index in data.index:
            for i in self._subscriptions:
                volume = data.loc[index]['volume:{}'.format(i.name)]
                price = data.loc[index]['close:{}'.format(i.name)]

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
```

#### Synthetic Exchange
We provide a sythetic exchange for testing. This exchange produces a variety of equity instruments, and simulates a complete exchange. This exchange runs on the `aat`'s `OrderBook` instance, which supports the following order types:

- Market orders
- Limit orders
- Stop orders

and order flags:
- Fill or kill
- All or none
- Immediate or cancel

The `OrderBook` api is as follows:

```python3
class OrderBook(object):
    '''A limit order book.

    Supports the following order types:
        - [x] market
            - [x] executes the entire volume
            - [ ] if notional specified, will execute (price*volume) worth (e.g. relies on total price, not volume)

            Flags:
                - [x] no flag
                - [x] fill-or-kill: entire order must fill against current book, otherwise nothing fills
                - [x] all-or-none: entire order must fill against 1 order, otherwise nothing fills
                - [x] immediate-or-cancel: same as fill or kill

        - [x] limit
            - [x] either puts on book or crosses spread, by default puts remainder on book

            Flags:
                - [x] no flag
                - [x] fill-or-kill: entire order must fill against current book, otherwise cancelled
                - [x] all-or-none: entire order must fill against 1 order, otherwise cancelled
                - [x] immediate-or-cancel: whenever this order executes, fill whatever fills and cancel remaining

        - [x] stop-market
            - 0 volume order, but when crosses triggers the submission of a market order
        - [x] stop-limit
            - 0 volume order, but when crosses triggers the submission of a market order

    Supports the following order flags:
        - [x] no flag
        - [x] fill-or-kill
        - [x] all-or-none
        - [x] immediate-or-cancel

    Args:
        instrument (Instrument): the instrument for the book
        exchange_name (str): name of the exchange
        callback (Function): callback on events
    '''
    def add(self, order):
        '''add a new order to the order book, potentially triggering events:
            EventType.TRADE: if this order crosses the book and fills orders
            EventType.FILL: if this order crosses the book and fills orders
            EventType.CHANGE: if this order crosses the book and partially fills orders
        Args:
            order (Data): order to submit to orderbook
        '''

    def change(self, order):
        '''modify an order on the order book, potentially triggering events:
            EventType.CHANGE: the change event for this
        Args:
            order (Data): order to submit to orderbook
        '''

    def cancel(self, order):
        '''remove an order from the order book, potentially triggering events:
            EventType.CANCEL: the cancel event for this
        Args:
            order (Data): order to submit to orderbook
        '''

    def find(self, order):
        '''find an order in the order book
        Args:
            order (Data): order to find in orderbook
        '''

    def topOfBook(self):
        '''return top of both sides

        Args:

        Returns:
            value (dict): returns {BUY: tuple, SELL: tuple}
        '''

    def spread(self):
        '''return the spread

        Args:

        Returns:
            value (float): spread between bid and ask
        '''

    def level(self, level: int = 0, price: float = None):
        '''return book level

        Args:
            level (int): depth of book to return
            price (float): price level to look for
        Returns:
            value (tuple): returns ask or bid if Side specified, otherwise ask,bid
        '''

    def levels(self, levels=0):
        '''return book levels starting at top

        Args:
            levels (int): number of levels to return
        Returns:
            value (dict of list): returns {"ask": [levels in order], "bid": [levels in order]} for `levels` number of levels
        '''
```

We can also run the `SyntheticExchange` as a service behind websockets to serve as a nice sandbox for testing strategies, building visualizations, etc. To do so, we can run the `aat-synthetic-server` command.

## Setting up and running
`aat` is setup to run off a configuration file. In this file, we specify some global parameters such as the `TradingType`, as well as configure the `Strategy` and `Exchange` instances.

Let us consider the simple example of the `BuyAndHold` strategy provided above, configured to run in `backtest` mode against the `SyntheticExchange` provided above. Such a configuration file would look like:

```bash
 > cat myconfig.cfg
[general]
verbose=0
trading_type=backtest

[exchange]
exchanges=
    aat.exchange:SyntheticExchange

[strategy]
strategies = 
    aat.strategy.sample:BuyAndHoldStrategy
```

We can run this configuration by running:
`aat myconfig.cfg`

### Trading Type
There are several values for the `TradingType` field:

- `live` - live trading against the exchange
- `simulation` - live trading against the exchange, but with order entry disabled
- `sandbox` - live trading against the exchange's sandbox or paper trading instance
- `backtest` - offline trading against historical OHLCV data

To test our strategy in any mode, we may need to setup exchange-specific keys to get historical data, stream market data, and make new orders.


### Strategies and Exchanges
We can run any number of strategies against any number of exchanges, including custom user-defined strategies and exchanges not implemented in the core `aat` repository. `aat` will multiplex the event streams and your strategies control which instruments they trade against which exchanges. 


| Exchange  | Market Data | Order Entry  |  TradingTypes | Asset Classes |
|---|---|---|---|---|
| Synthetic | Yes | Yes | Simulation,Backtest  | Equity |
| IEX | Yes | Fake | Live, Simulation, Sandbox, Backtest | Equity |
| InteractiveBrokers | In Progress | Yes |  Live, Simulation, Sandbox | Equity, Option, Future, Commodities, Spreads, Pair |
| TD Ameritrade | In Progress | In Progress | Equity, Option |
| Alpaca | In Progress | In Progress |   |
| Coinbase | In Progress | In Progress |  |
| Gemini | In Progress | In Progress |  |
| Coinbase | In Progress | In Progress |  |
| ccxt | In Progress | In Progress |  |

# TODO below here are sections that still need to be documented

## Core Data Structures

### Enums

### Models

### Instruments

## Other Features

### Trade/Portfolio Analysis
![](https://raw.githubusercontent.com/AsyncAlgoTrading/aat/master/docs/img/tearsheet.png)

![](https://raw.githubusercontent.com/AsyncAlgoTrading/aat/master/docs/img/rethist.png)


### API Access

### Risk Management

### Execution