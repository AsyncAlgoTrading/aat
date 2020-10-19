from datetime import datetime
from functools import lru_cache
# from aat import Instrument, InstrumentType, Account, Position
from aat import Instrument, InstrumentType, Position


@lru_cache(None)
def _get_currency(symbol):
    return Instrument(name=symbol, type=InstrumentType.CURRENCY)


@lru_cache(None)
def _get_accounts(client, exchange):
    ret = []
    accounts = client.accounts()

    for account in accounts:
        acc_data = client.account(account['id'])
        if acc_data['trading_enabled'] and float(acc_data['balance']) > 0:
            # acc = Account(account['id'], exchange, [
            pos = Position(float(acc_data['balance']),
                           0.,
                           datetime.now(),
                           Instrument(acc_data['currency'],
                                      InstrumentType.CURRENCY,
                                      exchange=exchange),
                           exchange,
                           []
                           )
            ret.append(pos)
            # ]
            # )
            # ret.append(acc)
    return ret
