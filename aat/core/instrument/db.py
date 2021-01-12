from typing import Dict, Optional, Tuple, List, TYPE_CHECKING
from ..exchange import ExchangeType
from ...config import InstrumentType

if TYPE_CHECKING:
    # Circular import
    from . import Instrument


class InstrumentDB(object):
    """instrument registration"""

    def __init__(self) -> None:
        self._by_name: Dict[str, List["Instrument"]] = {}
        self._by_type: Dict[Tuple[str, InstrumentType], List["Instrument"]] = {}
        self._by_exchange: Dict[Tuple[str, ExchangeType], "Instrument"] = {}
        self._by_type_and_exchange: Dict[
            Tuple[str, InstrumentType, ExchangeType], "Instrument"
        ] = {}

    def add(self, instrument: "Instrument") -> None:
        if instrument.name not in self._by_name:
            self._by_name[instrument.name] = [instrument]
            self._by_type[instrument.name, instrument.type] = [instrument]
        else:
            self._by_name[instrument.name].append(instrument)
            self._by_type[instrument.name, instrument.type].append(instrument)

        self._by_exchange[instrument.name, instrument.exchange] = instrument
        self._by_type_and_exchange[
            instrument.name, instrument.type, instrument.exchange
        ] = instrument

    def instruments(
        self,
        name: str = "",
        type: InstrumentType = InstrumentType.EQUITY,
        exchange: Optional[ExchangeType] = ExchangeType(""),
        *args: Tuple,
        **kwargs: Dict
    ) -> List["Instrument"]:
        ret = [inst for values in self._by_name.values() for inst in values]
        if not name and not type and not exchange:
            return ret
        if name:
            ret = [r for r in ret if r.name == name]
        if type:
            ret = [r for r in ret if r.type == type]
        if exchange:
            ret = [r for r in ret if exchange in r.exchanges]
        return ret

    def get(
        self,
        name: str = "",
        type: InstrumentType = InstrumentType.EQUITY,
        exchange: Optional[ExchangeType] = ExchangeType(""),
        *args: Tuple,
        **kwargs: Dict
    ) -> Optional["Instrument"]:
        """Like `instruments` but only returns 1"""
        ret = [inst for values in self._by_name.values() for inst in values]
        if name:
            ret = [r for r in ret if r.name == name]
        if type:
            ret = [r for r in ret if r.type == type]
        if exchange:
            ret = [r for r in ret if exchange in r.exchanges]
        return ret[0] if ret else None
