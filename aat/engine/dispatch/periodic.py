from typing import Callable, Awaitable, List
from temporalcache.utils import should_expire  # type: ignore


class Periodic(object):
    def __init__(self, loop, last_ts, function, second, minute, hour):
        self._loop = loop
        self._function: Callable[Awaitable[None]] = function
        self._second = second
        self._minute = minute
        self._hour = hour

        self._last = last_ts
        self._continue = True

    def stop(self) -> None:
        self._continue = False

    def expires(self, timestamp):
        return should_expire(self._last, timestamp, self._second, self._minute, self._hour)

    async def execute(self, timestamp):
        if self.expires(timestamp):
            await self._function()
            self._last = timestamp


class PeriodicManagerMixin(object):
    _periodics: List[Periodic] = []

    def periodics(self):
        return self._periodics

    def periodicIntervals(self) -> int:
        '''return the interval required for periodics, to optimize call times
        1 - secondly
        60 - minutely
        3600 - hourly
        '''
        ret = 3600
        for p in self._periodics:
            if p._second == '*':
                # if any secondly, return 0 right away
                return 1
            elif p._minute == '*':
                # if any require minutely, drop to 1
                ret = 60
        return ret
