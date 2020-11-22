from ..common import _in_cpp
from .parser import parseConfig, getStrategies, getExchanges  # noqa: F401

if _in_cpp():
    from ..binding import (  # noqa: F401
        TradingTypeCpp as TradingType,  # type: ignore
        SideCpp as Side,
        InstrumentTypeCpp as InstrumentType,
        EventTypeCpp as EventType,
        DataTypeCpp as DataType,
        OrderTypeCpp as OrderType,
        OrderFlagCpp as OrderFlag,
        ExitRoutineCpp as ExitRoutine,
    )
else:
    from .enums import (  # noqa: F401
        TradingType,
        Side,
        InstrumentType,
        EventType,
        DataType,
        OrderFlag,
        OrderType,
        OptionType,
        ExitRoutine,
    )
