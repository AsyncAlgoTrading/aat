# type: ignore
import pytest
from aat.common import _in_cpp
from aat.core import Order, Instrument, ExchangeType

_INSTRUMENT = Instrument("TE.ST")


class TestOrder:
    def test_stop_order_validation(self):
        if _in_cpp():
            return

        with pytest.raises(AssertionError):
            Order(
                volume=0.0,
                price=5.0,
                side=Order.Sides.SELL,
                exchange=ExchangeType(""),
                order_type=Order.Types.STOP,
                stop_target=Order(
                    volume=0.5,
                    price=5.0,
                    side=Order.Sides.SELL,
                    exchange=ExchangeType(""),
                    order_type=Order.Types.STOP,
                    instrument=_INSTRUMENT,
                ),
                instrument=_INSTRUMENT,
            )
