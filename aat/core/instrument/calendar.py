from datetime import time
from typing import Optional, Tuple, Union, cast

from aat.common import AATException
from pytz import UTC


class TradingDay(object):
    """Construct a representation of an instrument's trading day

    Args:
        open_times (Union[time, Tuple[time]]): time or tuple of times representing the time/s of market open. If missing tzinfo, will assume UTC.
        close_times (Union[time, Tuple[time]]): time or tuple of times representing the time/s of market close.  If missing tzinfo, will assume UTC.
    """

    __slots__ = [
        "_open_times",
        "_close_times",
    ]

    def __init__(
        self,
        open_times: Optional[Union[time, Tuple[time, ...]]] = None,
        close_times: Optional[Union[time, Tuple[time, ...]]] = None,
    ):
        if open_times and not isinstance(open_times, (tuple, time)):
            # raise exception if wrong type
            raise AATException(
                "`open_times` must be time or tuple of times, got: {}".format(
                    type(open_times)
                )
            )
        elif isinstance(open_times, time):
            # force tuple
            open_times = cast(Tuple[time, ...], (open_times,))

        if open_times:
            # force tz
            open_times = tuple(
                tm if tm.tzinfo else time(tm.hour, tm.minute, tzinfo=UTC)
                for tm in open_times
            )

        self._open_times: Optional[Tuple[time, ...]] = open_times

        if close_times and not isinstance(close_times, (tuple, time)):
            # raise exception if wrong type
            raise AATException(
                "`close_times` must be time or tuple of times, got: {}".format(
                    type(close_times)
                )
            )
        elif isinstance(close_times, time):
            # force tuple
            close_times = cast(Tuple[time, ...], (close_times,))

        if close_times:
            # force tz
            close_times = tuple(
                tm if tm.tzinfo else time(tm.hour, tm.minute, tzinfo=UTC)
                for tm in close_times
            )

        self._close_times: Optional[Tuple[time, ...]] = close_times

    @property
    def open(self) -> Optional[Tuple[time, ...]]:
        return self._open_times

    @property
    def close(self) -> Optional[Tuple[time, ...]]:
        return self._close_times

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TradingDay):
            return False
        return self.open == other.open and self.close == other.close
