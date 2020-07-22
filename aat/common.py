import os
import itertools


def _in_cpp():
    try:
        from aat.binding import (SideCpp, EventTypeCpp, DataTypeCpp, InstrumentTypeCpp,  # type: ignore # noqa: F401
                                 OrderTypeCpp, OrderFlagCpp, OrderBookCpp, ExchangeTypeCpp,  # noqa: F401
                                 InstrumentCpp, DataCpp, EventCpp, OrderCpp, TradeCpp)  # noqa: F401
    except ImportError:
        if os.environ.get('AAT_USE_CPP', '') in ('1', 'ON'):
            # raise if being told to use c++
            raise
        return False

    return os.environ.get('AAT_USE_CPP', '').lower() in ('1', 'ON')


__c = itertools.count()
def _gen_id(): return next(__c)  # noqa: E731
