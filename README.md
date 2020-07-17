# AAT
AsyncAlgoTrading

[![Build Status](https://dev.azure.com/tpaine154/aat/_apis/build/status/AsyncAlgoTrading.aat?branchName=master)](https://dev.azure.com/tpaine154/aat/_build/latest?definitionId=19&branchName=master)
[![Coverage](https://img.shields.io/azure-devops/coverage/tpaine154/aat/19/master)](https://dev.azure.com/tpaine154/aat/_apis/build/status/AsyncAlgoTrading.aat?branchName=master)
[![License](https://img.shields.io/github/license/timkpaine/aat.svg)](https://pypi.python.org/pypi/aat)
[![PyPI](https://img.shields.io/pypi/v/aat.svg)](https://pypi.python.org/pypi/aat)
[![Docs](https://img.shields.io/readthedocs/aat.svg)](http://aat.readthedocs.io/en/latest/)
 
`aat` is a framework for writing algorithmic trading strategies in python. It is designed to be modular and extensible, and is the core engine powering [AlgoCoin](https://github.com/asyncalgotrading/algo-coin).

It comes with support for live trading across (and between) multiple exchanges, fully integrated backtesting support, slippage and transaction cost modeling, and robust reporting and risk mitigation through manual and programatic algorithm controls.

Like Zipline, the inspiration for this system, `aat` exposes a single strategy class which is utilized for both live trading and backtesting. The strategy class is simple enough to write and test algorithms quickly, but extensible enough to allow for complex slippage and transaction cost modeling, as well as mid- and post- trade analysis.  


# Overview
`aat` is composed of 4 major parts. 

- trading engine
- risk management engine
- execution engine
- backtest engine

## Trading Engine
The trading engine initializes all exchanges and strategies, then martials data, trade requests, and trade responses between the strategy, risk, execution, and exchange objects, while keeping track of high-level statistics on the system

## Risk Management Engine
The risk management engine enforces trading limits, making sure that stategies are limited to certain risk profiles. It can modify or remove trade requests prior to execution depending on user preferences and outstanding positions and orders.

## Execution engine
The execution engine is a simple passthrough to the underlying exchanges. It provides a unified interface for creating various types of orders.

## Backtest engine
The backtest engine provides the ability to run the same stragegy offline against historical data.

# Trading Strategy
The core element of `aat` is the trading strategy interface. It includes both data processing and order management functionality. Users subclass this class in order to implement their strategies

## Class
```python3
class Strategy(metaclass=ABCMeta):
    @abstractmethod
    def onTrade(self, event: Event):
        '''Called whenever a `Trade` event is received'''

    def onOpen(self, event: Event):
        '''Called whenever an Order `Open` event is received'''

    def onFill(self, event: Event):
        '''Called whenever an Order `Fill` event is received'''

    def onCancel(self, event: Event):
        '''Called whenever an Order `Cancel` event is received'''

    def onChange(self, event: Event):
        '''Called whenever an Order `Change` event is received'''

    def onError(self, event: Event):
        '''Called whenever an internal error occurs'''

    def onStart(self):
        '''Called once at engine initialization time'''

    def onExit(self):
        '''Called once at engine exit time'''

    def onHalt(self, data):
        '''Called whenever an exchange `Halt` event is received, i.e. an event to stop trading'''

    def onContinue(self, data):
        '''Called whenever an exchange `Continue` event is received, i.e. an event to continue trading'''
```

## Example Strategy
Here is a simple trading strategy that buys once and holds. 

```python3
from aat import Strategy, Event, Order, Trade, Side

class BuyAndHoldStrategy(Strategy):
    def __init__(self, *args, **kwargs) -> None:
        super(BuyAndHoldStrategy, self).__init__(*args, **kwargs)

    async def onStart(self, event: Event) -> None:
        '''subscribe to one of the available instruments'''
        self.subscribe(self.instruments()[0])

    async def onTrade(self, event: Event) -> None:
        '''Called whenever a `Trade` event is received'''

        # no past trades, no current orders
        if not self.orders(event.target.instrument) and not self.trades(event.target.instrument):
            req = Order(side=Side.BUY,
                        price=event.target.price + 10,
                        volume=1,
                        instrument=event.target.instrument,
                        order_type=Order.Types.MARKET,
                        exchange=event.target.exchange)
            print("requesting buy : {}".format(req))
            await self.newOrder(req)

    async def onBought(self, event: Event) -> None:
        print('bought {:.2f} @ {:.2f}'.format(event.target.volume, event.target.price))

    async def onReject(self, event: Event) -> None:
        print('order rejected')
        import sys
        sys.exit(0)
```

Trading strategies have only one required method handling messages:

- onTrade: Called when a trade occurs

There are other optional callbacks for more granular processing:

- onOpen: Called when a new order occurs
- onFill: Called when a strategy's trade executes
- onCancel: Called when an order is cancelled
- onChange: Called when an order is modified
- onError: Called when a system error occurs
- onHalt: Called when trading is halted
- onContinue: Called when trading continues
- onStart: Called when the program starts
- onExit: Called when the program shuts down

There are several callbacks for order entry:
- onBought:
- onSold:
- onRejected:

There are several methods for order entry and data subscriptions:

- subscribe: subscribe to an instrument/exchange data
- instruments: get available instruments
- newOrder: submit a new order
- buy  (alias of newOrder): submit a new order
- sell (alias of newOrder): submit a new order
- orders: get open orders
- pastOrders: get past orders
- trades: get past trades
- positions: get position informatino
- risk: get risk information

There are also several optional callbacks for backtesting:

- slippage
- transactionCost

## Setting up and running
An instance of `TradingStrategy` class is able to run live or against a set of historical trade/quote data. When instantiating a `TradingEngine` object, you can set a `type` attribute to be one of:

- `live` - live trading against the exchange
- `simulation` - live trading against the exchange, but with order entry disabled
- `sandbox` - live trading against the exchange's sandbox instance
- `backtest` - offline trading against historical OHLCV data

To test our strategy in any mode, we will need to setup exchange keys to get historical data, stream market data, and make new orders.

### Synthetic Exchange
We provide a sythetic exchange for testing

TODO more docs

### API Keys
You should creat API keys for exchanges you wish to trade on. For this example, we will assume a Coinbase Pro account with trading enabled. I usually put my keys in a set of shell scripts that are gitignored, so I don't post anything by accident. My scripts look something like:

```bash
export COINBASE_API_KEY=...
export COINBASE_API_SECRET=...
export COINBASE_API_PASS=...
```

Prior to running, I source the keys I need. 

### Sandboxes
Currently only the Gemini sandbox is supported, the other exchanges have discontinued theirs. To run in sandbox, set `TradingEngine.type` to Sandbox.

### Live Trading
When you want to run live, set `TradingEngine.type` to Live. You will want to become familiar with the risk and execution engines, as these control things like max drawdown, max risk accrual, execution eagerness, etc.

### Simulation Trading
When you want to run an algorithm live, but don't yet trust that it can make money, set `TradingEngine.type` to simulation. This will let it run against real money, but disallow order entry. You can then set things like slippage and transaction costs as you would in a backtest.

### Testing
Because there are a variety of options, a config file is generally the most usable interface for configuration. Here is an example configuration for backtesting the Buy-and-hold strategy above on a synthetic exchange:

```bash
> cat backtest.cfg
[general]
verbose=0
api=0
trading_type=backtest

[exchange]
exchanges=
    aat.exchange:SyntheticExchange

[strategy]
strategies = 
    aat.strategy.sample.buy_and_hold:BuyAndHoldStrategy

[risk]
max_drawdown = 100.0
max_risk = 100.0
total_funds = 10.0
```

## Extending
Apart from writing new strategies, this library can be extended by adding new exchanges. These are pretty simple. For cryptocurrency exchanges, I rely heavily on `ccxt`, `asyncio`, and websocket libraries.

### Example
Here is the coinbase exchange. Most of the code is to manage different websocket subscription options, and to convert between `aat`, `ccxt` and exchange-specific formatting of things like symbols, order types, etc. 
```python3
class CoinbaseExchange(Exchange):
```

# Core Elements

## TradingEngine

## Data Classes

### Data

### Event

## Instrument and Trade Models

### Instrument

### Trade

## Exchange

### Orderbook
We implement a full limit-order book, supporting the following order types:

#### Market
Executes the entire volume. If price specified, will execute (price*volume) worth (e.g. relies on total price, not volume)

#### Limit:
Either puts the order on the book,  or crosses spread triggering a trade. By default puts remainder of unexecuted volume on book.

#### Stop-Market
When trade prices cross the target price, triggers a market order.

#### Stop-Limit
When trade prices cross the target price, triggers a limit order.

#### Flags
We support a number of order flags for Market and Limit orders:

- No Flag: default behavior for the given order type
- Fill-Or-Kill:
    - Market Order: entire order must fill against current book, otherwise nothing fills
    - Limit Order: entire order must fill against current book, otherwise nothing fills and order cancelled
- All-Or-None:
    - Market Order: entire order must fill against 1 order on the book, otherwise nothing fills
    - Limit Order: entire order must fill against 1 order, otherwise nothing filled and order cancelled

- Immediate-Or-Cancel:
    - Market Order: same as fill or kill
    - Limit Order: whenever this order executes, fill whatever fills and cancel remaining

