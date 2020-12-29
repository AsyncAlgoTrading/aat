from aat.core import ExchangeType, Instrument, TradingDay


class TestInstrumentCalendar(object):
    def test_instrument_calendar(self):
        TradingDay()

    def test_instrument_calendar(self):
        t = TradingDay()
        e = ExchangeType("test-exchange")

        i = Instrument(
            "test",
            exchange=e,
            trading_day=t,
        )

        assert i.tradingDay(e) == t
