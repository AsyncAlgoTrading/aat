import asyncio
from datetime import datetime
from typing import List, Callable, Union, Optional, TYPE_CHECKING

from aat.core import Instrument
from aat.exchange import Exchange
from aat.config import InstrumentType, TradingType

from .periodic import Periodic

if TYPE_CHECKING:
    from aat.engine import TradingEngine


class StrategyManagerUtilsMixin(object):
    _engine: 'TradingEngine'
    _exchanges: List[Exchange]
    _periodics: List[Periodic]

    #################
    # Other Methods #
    #################

    def tradingType(self) -> TradingType:
        return self._engine.trading_type

    def loop(self):
        return self._engine.event_loop

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

    async def lookup(self, instrument: Optional[Instrument], exchange=None):
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

    def _make_async(self, function):
        async def _wrapper():
            return await self.loop().run_in_executor(self._engine, self._engine.executor, function)
        return _wrapper

    def periodic(self,
                 function: Callable,
                 second: Union[int, str] = 0,
                 minute: Union[int, str] = '*',
                 hour: Union[int, str] = '*') -> Periodic:
        '''periodically run a given async function. NOTE: precise timing
        is NOT guaranteed due to event loop scheduling.'''
        if not self.loop().is_running():
            raise Exception('Install periodics after engine start (e.g. in `onStart`)')

        # Validation
        if not asyncio.iscoroutinefunction(function):
            function = self._make_async(function)

        if not isinstance(second, (int, str)):
            raise Exception('`second` arg must be int or str')

        if not isinstance(minute, (int, str)):
            raise Exception('`minute` arg must be int or str')

        if not isinstance(hour, (int, str)):
            raise Exception('`hour` arg must be int or str')

        if isinstance(second, str) and second != '*':
            raise Exception('Only "*" or int allowed for argument `second`')
        elif isinstance(second, str):
            second = None  # type: ignore
        elif second < 0 or second > 60:
            raise Exception('`second` must be between 0 and 60')

        if isinstance(minute, str) and minute != '*':
            raise Exception('Only "*" or int allowed for argument `minute`')
        elif isinstance(minute, str):
            minute = None  # type: ignore
        elif minute < 0 or minute > 60:
            raise Exception('`minute` must be between 0 and 60')

        if isinstance(hour, str) and hour != '*':
            raise Exception('Only "*" or int allowed for argument `hour`')
        elif isinstance(hour, str):
            hour = None  # type: ignore
        elif hour < 0 or hour > 24:
            raise Exception('`hour` must be between 0 and 24')
        # End Validation

        periodic = Periodic(self.loop(), self._engine._latest, function, second, minute, hour)
        self._periodics.append(periodic)
        return periodic
