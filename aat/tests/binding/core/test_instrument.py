from aat.binding import Instrument, InstrumentType


class TestInstrumentBinding:
    def test_init(self):
        i = Instrument("Test", InstrumentType.EQUITY)
        assert str(i) == "(Test-EQUITY)"
