from aat.exchange import Exchange
from aat.core import ExchangeType


class Kafka(Exchange):
    '''Kafka Exchange'''

    def __init__(self, trading_type, verbose):
        super().__init__(ExchangeType('kafka'))
        self._trading_type = trading_type
        self._verbose = verbose


Exchange.registerExchange('kafka', Kafka)
