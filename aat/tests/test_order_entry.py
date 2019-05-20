import os
from mock import patch


class TestOrderEntry:
    def setup(self):
        # setup() before each test method
        from aat.config import ExchangeConfig
        from aat.enums import TradingType, ExchangeType, PairType

        os.environ['GEMINI_API_KEY'] = 'test'
        os.environ['GEMINI_API_SECRET'] = 'test'
        os.environ['GEMINI_API_PASS'] = 'test'

        self.ec = ExchangeConfig(exchange_types=[ExchangeType.GEMINI],
                                 trading_type=TradingType.LIVE,
                                 currency_pairs=[PairType.BTCUSD])
