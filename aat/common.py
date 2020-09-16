import os
import itertools
import functools


@functools.lru_cache()
def _in_cpp():
    _cpp = os.environ.get('AAT_USE_CPP', '').lower() in ('1', 'on')

    try:
        from aat.binding import (SideCpp, EventTypeCpp, DataTypeCpp, InstrumentTypeCpp,  # type: ignore # noqa: F401
                                 OrderTypeCpp, OrderFlagCpp, OrderBookCpp, ExchangeTypeCpp,  # noqa: F401
                                 InstrumentCpp, DataCpp, EventCpp, OrderCpp, TradeCpp)  # noqa: F401
    except ImportError:
        if _cpp:
            # raise if being told to use c++
            raise
        return False

    return _cpp


def id_generator():
    __c = itertools.count()

    def _gen_id():
        return next(__c)
    return _gen_id
