# type: ignore
import pydantic
import pytest
from datetime import datetime

from aat.core import Order, Instrument
_INSTRUMENT = Instrument('TE.ST')


class TestOrder:
    def test_stop_order_validation(self):
        with pytest.raises(pydantic.ValidationError):
            Order(id=1,
                  timestamp=datetime.now().timestamp(),
                  volume=0.0,
                  price=5.0,
                  side=Order.Sides.SELL,
                  order_type=Order.Types.STOP_LIMIT,
                  stop_target=Order(
                      id=1,
                      timestamp=datetime.now().timestamp(),
                      volume=0.5,
                      price=5.0,
                      side=Order.Sides.SELL,
                      order_type=Order.Types.MARKET,
                      instrument=_INSTRUMENT,
                  ),
                  instrument=_INSTRUMENT)

        with pytest.raises(pydantic.ValidationError):
            Order(id=1,
                  timestamp=datetime.now().timestamp(),
                  volume=0.0,
                  price=5.0,
                  side=Order.Sides.SELL,
                  order_type=Order.Types.STOP_MARKET,
                  stop_target=Order(
                      id=1,
                      timestamp=datetime.now().timestamp(),
                      volume=0.5,
                      price=5.0,
                      side=Order.Sides.SELL,
                      instrument=_INSTRUMENT,
                  ),
                  instrument=_INSTRUMENT)
