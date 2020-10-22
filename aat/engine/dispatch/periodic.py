from typing import Callable, Awaitable
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

    async def execute(self, timestamp):
        if should_expire(self._last, timestamp, self._second, self._minute, self._hour):
            await self._function()
            self._last = timestamp
