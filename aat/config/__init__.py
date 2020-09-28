from ..common import _in_cpp
from .parser import parseConfig, getStrategies, getExchanges  # noqa: F401

if _in_cpp():
    from ..binding import (TradingTypeCpp as TradingType,
                           SideCpp as Side,
                           InstrumentTypeCpp as InstrumentType,
                           EventTypeCpp as EventType,
                           DataTypeCpp as DataType,
                           OrderTypeCpp as OrderType,
                           OrderFlagCpp as OrderFlag,
                           ExitRoutineCpp as ExitRoutine)  # type: ignore # noqa: F401
else:
    from .enums import TradingType, Side, InstrumentType, EventType, DataType, OrderFlag, OrderType, OptionType, ExitRoutine  # noqa: F401
