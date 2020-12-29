from typing import Dict, Optional, Tuple, List, TYPE_CHECKING
from ..exchange import ExchangeType
from ...config import InstrumentType

if TYPE_CHECKING:
    # Circular import
    from . import Instrument


class InstrumentDB(object):
    """instrument registration"""

    def __init__(self) -> None:
        self._name_map: Dict[str, "Instrument"] = {}
        self._map: Dict[Tuple[str, InstrumentType], "Instrument"] = {}

    def add(self, instrument: "Instrument") -> None:
        if instrument.name in self._name_map:
            return
        self._name_map[instrument.name] = instrument
        self._map[instrument.name, instrument.type] = instrument

    def instruments(
        self,
        name: str = "",
        type: InstrumentType = InstrumentType.EQUITY,
        exchange: Optional[ExchangeType] = ExchangeType(""),
        *args: Tuple,
        **kwargs: Dict
    ) -> List["Instrument"]:
        if not name and not type and not exchange:
            return list(self._map.values())
        elif name:
            inst = self._name_map.get(name, None)
            return [inst] if inst else []

        ret = list(self._map.values())
        if type:
            ret = [r for r in ret if r.type == type]
        if exchange:
            ret = [r for r in ret if exchange in r.exchanges]
        return ret

    def get(
        self,
        name: str = "",
        type: InstrumentType = InstrumentType.EQUITY,
        exchange: ExchangeType = ExchangeType(""),
        *args: Tuple,
        **kwargs: Dict
    ) -> "Instrument":
        return self._name_map[name]


# TODO allow for multiple exchange's distinct instrument representation
