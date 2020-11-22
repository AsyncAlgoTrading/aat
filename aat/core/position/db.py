from typing import Mapping, Tuple, Union, TYPE_CHECKING
from ..exchange import ExchangeType
from ..instrument import Instrument
from ...config import InstrumentType

if TYPE_CHECKING:
    # Circular import
    from . import Position, CashPosition


class PositionDB(object):
    """Position registration"""

    def __init__(self):
        self._inst_map: Mapping[Instrument, Union[Position, CashPosition]] = {}
        self._exch_map: Mapping[
            Tuple[ExchangeType, Instrument], Union[Position, CashPosition]
        ] = {}

    def add(self, position):
        pass

    def positions(
        self,
        name="",
        type: InstrumentType = InstrumentType.CURRENCY,
        exchange: ExchangeType = ExchangeType(""),
        *args,
        **kwargs
    ):
        pass

    def get(
        self,
        name="",
        type: InstrumentType = InstrumentType.CURRENCY,
        exchange: ExchangeType = ExchangeType(""),
        *args,
        **kwargs
    ):
        pass
