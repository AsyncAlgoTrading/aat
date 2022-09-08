from aat.exchange import Exchange
from aat.config import TradingType
from aat.core import ExchangeType


class Kafka(Exchange):
    """Kafka Exchange"""

    def __init__(self, trading_type: TradingType, verbose: bool) -> None:
        super().__init__(ExchangeType("kafka"))
        self._trading_type = trading_type
        self._verbose = verbose
