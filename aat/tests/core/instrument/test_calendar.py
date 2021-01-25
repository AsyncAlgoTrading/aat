import pytest
from aat.core import ExchangeType, Instrument, TradingDay


class TestInstrumentCalendar(object):
    def test_instrument_calendar(self):
        TradingDay()

    @pytest.mark.skipif("os.environ.get('AAT_USE_CPP', '')")
    def test_instrument_calendar_getter(self):
        t = TradingDay()
        e = ExchangeType("test-exchange")

        i = Instrument(
            "TestTradingDayInst",
            exchange=e,
            trading_day=t,
        )

        assert i.tradingDay == t
