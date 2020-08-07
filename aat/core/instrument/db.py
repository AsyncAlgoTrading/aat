from typing import Mapping, Tuple, TYPE_CHECKING
from ..exchange import ExchangeType
from ...config import InstrumentType

if TYPE_CHECKING:
    # Circular import
    from . import Instrument


class InstrumentDB(object):
    '''instrument registration'''

    def __init__(self):
        self._name_map: Mapping[str, 'Instrument'] = {}
        self._map: Mapping[Tuple[str, InstrumentType], 'Instrument'] = {}

    def add(self, instrument):
        if instrument.name in self._name_map:
            return
        self._name_map[instrument.name] = instrument
        self._map[instrument.name, instrument.type] = instrument

    def instruments(self,
                    name="",
                    type: InstrumentType = InstrumentType.EQUITY,
                    exchange: ExchangeType = ExchangeType(""),
                    *args,
                    **kwargs):
        if not name and not type and not exchange:
            return list(self._map.values())
        elif name:
            return self._name_map.get(name, None)

        ret = list(self._map.values())
        if type:
            ret = [r for r in ret if r.type == type]
        if exchange:
            ret = [r for r in ret if exchange in r.exchanges]
        return ret

    def get(self,
            name="",
            type: InstrumentType = InstrumentType.EQUITY,
            exchange: ExchangeType = ExchangeType(""),
            *args,
            **kwargs):
        return self._name_map[name]

# TODO allow for multiple exchange's distinct instrument representation
