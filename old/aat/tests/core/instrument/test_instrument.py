import pytest
from aat.core import ExchangeType, Instrument


class TestInstrument(object):
    @pytest.mark.skipif("os.environ.get('AAT_USE_CPP', '')")
    def test_instrument(self):
        E1 = ExchangeType("E1")
        E2 = ExchangeType("E2")
        E3 = ExchangeType("E3")

        i1 = Instrument(
            "TestInst",
            exchange=E1,
            broker_id="1",
        )

        i2 = Instrument(
            "TestInst",
            exchange=E2,
            broker_id="2",
            broker_exchange="test",
        )

        i3 = Instrument(
            "TestInst",
            exchange=E3,
            broker_id="3",
        )

        assert i1.tradingLines() == [i1, i2, i3]
        assert i2.tradingLines() == [i1, i2, i3]
        assert i3.tradingLines() == [i1, i2, i3]
