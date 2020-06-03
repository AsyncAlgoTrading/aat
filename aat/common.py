import os


def _in_cpp():
    try:
        from aat.binding import SideCpp, EventTypeCpp, DataTypeCpp, InstrumentTypeCpp, OrderTypeCpp, OrderFlagCpp, OrderBookCpp, ExchangeTypeCpp, InstrumentCpp, DataCpp, EventCpp, OrderCpp, TradeCpp
    except ImportError:
        return False

    return os.environ.get('AAT_USE_CPP', '').lower() in ('1', 'ON')
