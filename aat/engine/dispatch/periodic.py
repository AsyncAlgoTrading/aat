import asyncio
from datetime import datetime
from typing import Callable, Awaitable, List, Optional
from temporalcache.utils import should_expire  # type: ignore


class Periodic(object):
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        last_ts: datetime,
        function: Callable[..., Awaitable[None]],
        second: Optional[int],
        minute: Optional[int],
        hour: Optional[int],
    ) -> None:
        self._loop = loop
        self._function: Callable[..., Awaitable[None]] = function
        assert (
            second != "*" and minute != "*" and hour != "*"
        ), "Please use None instead of '*'"
        self.__second = second
        self.__minute = minute
        self.__hour = hour

        self._last = last_ts
        self._continue = True

    @property
    def second(self) -> Optional[int]:
        return self.__second

    @property
    def minute(self) -> Optional[int]:
        return self.__minute

    @property
    def hour(self) -> Optional[int]:
        return self.__hour

    def stop(self) -> None:
        self._continue = False

    def expires(self, timestamp: datetime) -> bool:
        return should_expire(self._last, timestamp, self.second, self.minute, self.hour)

    async def execute(self, timestamp: datetime) -> None:
        if self.expires(timestamp):
            await self._function(timestamp=timestamp)
            self._last = timestamp


class PeriodicManagerMixin(object):
    _periodics: List[Periodic] = []

    def periodics(self) -> List[Periodic]:
        return self._periodics

    def periodicIntervals(self) -> int:
        """return the interval required for periodics, to optimize call times
        1 - secondly
        60 - minutely
        3600 - hourly
        """
        ret = 3600
        for p in self._periodics:
            if p.second is None:
                # if any secondly, return 0 right away
                return 1
            elif p.minute is None:
                # if any require minutely, drop to 1
                ret = 60
        return ret
