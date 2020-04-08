from aat.config import InstrumentType
from aat.binding import InstrumentCpp


class TestInstrumentBinding:
    def test_init(self):
        i = InstrumentCpp("Test", InstrumentType.EQUITY)
        assert str(i) == "(Test-EQUITY)"
