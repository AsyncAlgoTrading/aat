import asyncio
from datetime import datetime
from typing import Optional, Union, List

import pytest

from aat.engine.dispatch import Periodic
from aat.engine.dispatch.periodic import PeriodicManagerMixin


class TestMixin(PeriodicManagerMixin):
    def __init__(self, periodic: Union[List[Periodic], Periodic]):
        if isinstance(periodic, Periodic):
            periodic = [periodic]
        self._periodics = periodic


class TestPeriodic:
    def create_periodic_mixin(
        self, second: Optional[int], minute: Optional[int], hour: Optional[int]
    ):
        async def noop():
            pass

        return Periodic(
            asyncio.get_event_loop(), datetime.now(), noop, second, minute, hour
        )

    def test_secondly_periodic(self):
        periodic = TestMixin(self.create_periodic_mixin(None, None, None))
        assert periodic.periodicIntervals() == 1

    def test_minutely_periodic(self):
        periodic = TestMixin(self.create_periodic_mixin(5, None, None))
        assert periodic.periodicIntervals() == 60

    def test_hourly_periodic(self):
        periodic = TestMixin(self.create_periodic_mixin(10, 2, None))
        assert periodic.periodicIntervals() == 3600

    def test_removal_of_asterisk(self):
        with pytest.raises(Exception):
            periodic = TestMixin(self.create_periodic_mixin("*", "*", "*"))
            periodic.periodicIntervals()
