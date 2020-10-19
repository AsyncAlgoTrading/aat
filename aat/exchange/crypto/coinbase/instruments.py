from functools import lru_cache
from aat import Instrument, InstrumentType, Side


@lru_cache(None)
def _get_currency(symbol):
    return Instrument(name=symbol, type=InstrumentType.CURRENCY)


@lru_cache(None)
def _get_instruments(client, exchange):
    ret = []

    products = client.products()

    for product in products:
        first = product['base_currency']
        second = product['quote_currency']
        ret.append(
            Instrument(name='{}/{}'.format(first, second),
                       type=InstrumentType.PAIR,
                       exchange=exchange,
                       brokerId=product['id'],
                       leg1=_get_currency(first),
                       leg2=_get_currency(second),
                       leg1_side=Side.BUY,
                       leg2_side=Side.SELL)
        )
    return ret
