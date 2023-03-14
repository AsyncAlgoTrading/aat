from typing import Optional, Dict, TYPE_CHECKING
from ...config import InstrumentType

if TYPE_CHECKING:
    # Circular import
    from .exchange import ExchangeType
    from ..instrument import Instrument


class ExchangeDB(object):
    """exchange registration"""

    def __init__(self) -> None:
        self._name_map: Dict[str, "ExchangeType"] = {}
        self._map: Dict["Instrument", "ExchangeType"] = {}

    def add(self, exchange: "ExchangeType") -> None:
        if exchange.name in self._name_map:
            return
        self._name_map[exchange.name] = exchange

    def instruments(
        self,
        name: str = "",
        type: InstrumentType = InstrumentType.EQUITY,
        exchange: ExchangeType = ExchangeType(""),
    ) -> None:
        raise NotImplementedError()

    def get(
        self, name: str = "", instrument: Optional["Instrument"] = None
    ) -> "ExchangeType":
        if name:
            return self._name_map[name]
        raise NotImplementedError()
