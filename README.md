<img src="https://raw.githubusercontent.com/AsyncAlgoTrading/aat/main/docs/img/icon.png" width="200px"></img>

[![Build Status](https://github.com/AsyncAlgoTrading/aat/workflows/Build%20Status/badge.svg?branch=main)](https://github.com/AsyncAlgoTrading/aat/actions?query=workflow%3A%22Build+Status%22)
[![Coverage](https://codecov.io/gh/AsyncAlgoTrading/aat/branch/main/graph/badge.svg)](https://codecov.io/gh/AsyncAlgoTrading/aat)
[![License](https://img.shields.io/github/license/timkpaine/aat.svg)](https://pypi.python.org/pypi/aat)
[![PyPI](https://img.shields.io/pypi/v/aat.svg)](https://pypi.python.org/pypi/aat)
[![Docs](https://img.shields.io/readthedocs/aat.svg)](http://aat.readthedocs.io/en/latest/)
 
`aat` is an asynchronous, event-driven framework for writing algorithmic trading strategies in python with optional acceleration in rust. It is designed to be modular and extensible, with support for a wide variety of instruments and strategies, live trading across (and between) multiple exchanges, fully integrated backtesting support, slippage and transaction cost modeling, and robust reporting and risk mitigation through manual and programatic algorithm controls.

Like [Zipline](https://github.com/quantopian/zipline) and [Lean](https://github.com/QuantConnect/Lean), `aat` exposes a single strategy class which is utilized for both live trading and backtesting. The strategy class is simple enough to write and test algorithms quickly, but extensible enough to allow for complex slippage and transaction cost modeling, as well as mid- and post- trade analysis.  

`aat` is in active use for live algorithmic trading on equities, commodity futures contracts, and commodity futures spreads by undisclosed funds.
