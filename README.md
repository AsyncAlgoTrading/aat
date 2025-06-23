
<img src="https://raw.githubusercontent.com/AsyncAlgoTrading/aat/main/docs/img/icon.png" width="200px"></img>

[![Build Status](https://github.com/AsyncAlgoTrading/aat/actions/workflows/build.yml/badge.svg)](https://github.com/AsyncAlgoTrading/aat/actions?query=workflow%3A%22Build+Status%22)
[![Coverage](https://codecov.io/gh/AsyncAlgoTrading/aat/branch/main/graph/badge.svg)](https://codecov.io/gh/AsyncAlgoTrading/aat)
[![License](https://img.shields.io/github/license/timkpaine/aat.svg)](https://github.com/AsyncAlgoTrading/aat/blob/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/aat.svg)](https://pypi.python.org/pypi/aat)
[![Docs](https://img.shields.io/readthedocs/aat.svg)](http://aat.readthedocs.io/en/latest/)
 
`aat` is an asynchronous, event-driven framework for writing algorithmic trading strategies in python with optional acceleration in C++. It is designed to be modular and extensible, with support for a wide variety of instruments and strategies, live trading across (and between) multiple exchanges, fully integrated backtesting support, slippage and transaction cost modeling, and robust reporting and risk mitigation through manual and programatic algorithm controls.

Like [Zipline](https://github.com/quantopian/zipline) and [Lean](https://github.com/QuantConnect/Lean), `aat` exposes a single strategy class which is utilized for both live trading and backtesting. The strategy class is simple enough to write and test algorithms quickly, but extensible enough to allow for complex slippage and transaction cost modeling, as well as mid- and post- trade analysis.  

`aat` is in active use for live algorithmic trading on equities, commodity futures contracts, and commodity futures spreads by undisclosed funds.

## Overview
A complete overview of the core components of `aat` is provided in the [GETTING_STARTED](GETTING_STARTED.md) file.

### Internals
`aat`'s engine is composed of 4 major parts. 

- trading engine
- risk management engine
- execution engine
- backtest engine


#### Trading Engine
The trading engine initializes all exchanges and strategies, then martials data, trade requests, and trade responses between the strategy, risk, execution, and exchange objects, while keeping track of high-level statistics on the system

#### Risk Management Engine
The risk management engine enforces trading limits, making sure that stategies are limited to certain risk profiles. It can modify or remove trade requests prior to execution depending on user preferences and outstanding positions and orders.

#### Execution engine
The execution engine is a simple passthrough to the underlying exchanges. It provides a unified interface for creating various types of orders.

#### Backtest engine
The backtest engine provides the ability to run the same stragegy offline against historical data.

### Core Components
`aat` has a variety of core classes and data structures, the most important of which are the `Strategy` and `Exchange` classes.

#### Trading Strategy
The core element of `aat` is the trading strategy interface. It includes both data processing and order management functionality. Users subclass this class in order to implement their strategies. Methods of the form `onNoun` are used to handle market data events, while methods of the form `onVerb` are used to handle order entry events. There are also a variety of order management and data subscription methods available.

The only method that is required to be implemented is the `onTrade` method. The full specification of a strategy is given in [GETTING_STARTED](GETTING_STARTED.md).


#### Other Components
`aat` also provides a complete limit-order book implementation, including flags like `fill-or-kill` and `all-or-nothing`, which is used to power the synthetic testing exchange.


## Support / Contributors
Thanks to the following organizations for providing code or financial support.

<a href="https://nemoulous.com"><img src="https://raw.githubusercontent.com/asyncalgotrading/aat/main/docs/img/nem.png" width="50"></a>

<a href="https://nemoulous.com">Nemoulous</a>

## License
This software is licensed under the Apache 2.0 license. See the [LICENSE](LICENSE) file for details.
