from typing import Mapping, TYPE_CHECKING
from ...config import InstrumentType

if TYPE_CHECKING:
    # Circular import
    from .exchange import ExchangeType
    from ..instrument import Instrument


class ExchangeDB(object):
    """exchange registration"""

    def __init__(self):
        self._name_map: Mapping[str, "ExchangeType"] = {}
        self._map: Mapping["Instrument", "ExchangeType"] = {}

    def add(self, exchange):
        if exchange.name in self._name_map:
            return
        self._name_map[exchange.name] = exchange

    def instruments(
        self,
        name="",
        type: InstrumentType = InstrumentType.EQUITY,
        exchange: ExchangeType = ExchangeType(""),
        *args,
        **kwargs
    ):
        raise NotImplementedError()

    def get(self, name="", instrument: "Instrument" = None, *args, **kwargs):
        if name:
            return self._name_map[name]
        raise NotImplementedError()
