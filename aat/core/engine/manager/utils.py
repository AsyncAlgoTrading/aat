from datetime import datetime
from typing import List

from aat.core import TradingEngine, Instrument
from aat.exchange import Exchange
from aat.config import InstrumentType, TradingType


class StrategyManagerUtilsMixin(object):
    _engine: TradingEngine
    _exchanges: List[Exchange]


    #################
    # Other Methods #
    #################
    def tradingType(self) -> TradingType:
        return self._engine.trading_type

    def now(self) -> datetime:
        '''Return the current datetime. Useful to avoid code changes between
        live trading and backtesting. Defaults to `datetime.now`'''
        return self._engine.now()

    def instruments(self, type: InstrumentType = None, exchange=None):
        '''Return list of all available instruments'''
        return Instrument._instrumentdb.instruments(type=type, exchange=exchange)

    async def subscribe(self, instrument=None, strategy=None):
        '''Subscribe to market data for the given instrument'''
        if strategy not in self._data_subscriptions:
            self._data_subscriptions[strategy] = []

        self._data_subscriptions[strategy].append(instrument)

        for exc in self._exchanges:
            await exc.subscribe(instrument)

    def dataSubscriptions(self, handler, event):
        '''does handler subscribe to the data for event'''
        if handler not in self._data_subscriptions:
            # subscribe all by default
            return True
        return event.target.instrument in self._data_subscriptions[handler]

    async def lookup(self, instrument: Instrument, exchange=None):
        '''Return list of all available instruments that match the instrument given'''
        if exchange in self._exchanges:
            return await exchange.lookup(instrument)

        elif exchange is None:
            ret = []
            for exchange in self._exchanges:
                ret.extend(await exchange.lookup(instrument))
            return ret

        # None implement
        raise NotImplementedError()
