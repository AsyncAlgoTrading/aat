# type: ignore
import os
import pytest
from collections import deque
from aat.core import Trade, Order, Instrument, ExchangeType


_INSTRUMENT = Instrument("TE.ST")


class TestTrade:
    def test_maker_orders_validation(self):
        if not os.environ.get("AAT_USE_CPP"):
            with pytest.raises(Exception):
                o = Order(
                    volume=0.0,
                    price=5.0,
                    side=Order.Sides.SELL,
                    order_type=Order.Types.LIMIT,
                    exchange=ExchangeType(""),
                    instrument=_INSTRUMENT,
                )
                Trade(maker_orders=deque(), taker_order=o)
