from ..exchange import ExchangeType
from ...config import InstrumentType


class InstrumentDB(object):
    '''instrument registration'''

    def __init__(self):
        self._name_map = {}
        self._map = {}

    def add(self, instrument):
        if instrument.name in self._name_map:
            return
        self._name_map[instrument.name] = instrument
        self._map[instrument.name, instrument.type] = instrument

    def instruments(self, name="", type: InstrumentType = InstrumentType.EQUITY, exchange: ExchangeType = ExchangeType("")):
        if not name and not type and not exchange:
            return list(self._map.values())
        elif name:
            return self._name_map.get(name, None)

        ret = list(self._map.values())
        if type:
            ret = [r for r in ret if ret.type == type]
        if exchange:
            ret = [r for r in ret if ret.exchange == exchange]
        return ret

    def get(self, name="", type: InstrumentType = InstrumentType.EQUITY, exchange: ExchangeType = ExchangeType("")):
        ret = self._name_map[name]
        if exchange not in ret.exchanges:
            ret.exchanges.append(exchange)
        return ret
