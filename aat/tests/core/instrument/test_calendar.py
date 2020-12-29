import os

import pytest
from aat.core import ExchangeType, Instrument, TradingDay


class TestInstrumentCalendar(object):
    def test_instrument_calendar(self):
        TradingDay()

    @pytest.mark.skipif(os.environ["AAT_USE_CPP"], "Not implemented yet")
    def test_instrument_calendar_getter(self):
        t = TradingDay()
        e = ExchangeType("test-exchange")

        i = Instrument(
            "test",
            exchange=e,
            trading_day=t,
        )

        assert i.tradingDay(e) == t
