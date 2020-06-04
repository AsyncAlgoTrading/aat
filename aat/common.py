import os


def _in_cpp():
    try:
        from aat.binding import (SideCpp, EventTypeCpp, DataTypeCpp, InstrumentTypeCpp,  # noqa: F401
                                 OrderTypeCpp, OrderFlagCpp, OrderBookCpp, ExchangeTypeCpp,  # noqa: F401
                                 InstrumentCpp, DataCpp, EventCpp, OrderCpp, TradeCpp)  # noqa: F401
    except ImportError:
        return False

    return os.environ.get('AAT_USE_CPP', '').lower() in ('1', 'ON')
