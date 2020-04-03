# type: ignore
import pytest
import pydantic
from datetime import datetime
from collections import deque
from aat.core import Trade, Order, Instrument


_INSTRUMENT = Instrument('TE.ST')


class TestTrade:
    def test_maker_orders_validation(self):
        with pytest.raises(pydantic.ValidationError):
            o = Order(id=1,
                      timestamp=datetime.now().timestamp(),
                      volume=0.0,
                      price=5.0,
                      side=Order.Sides.SELL,
                      order_type=Order.Types.LIMIT,
                      instrument=_INSTRUMENT)
            Trade(maker_orders=deque(), taker_order=o)
