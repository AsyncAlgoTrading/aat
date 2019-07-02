from mock import patch, MagicMock


class TestExchange:
    def test_init(self):
        from ...config import ExchangeConfig
        from ...exchanges.gemini import GeminiExchange
        from ...enums import ExchangeType

        with patch('os.environ'), patch('ccxt.gemini') as m:
            ec = ExchangeConfig()
            ec.exchange_type = ExchangeType.GEMINI
            m.get_balances.return_value = []
            e = GeminiExchange(ExchangeType.GEMINI, ec)
            e._running = True
            assert e

    def test_receive(self):
        from ...config import ExchangeConfig
        from ...exchanges.gemini import GeminiExchange
        from ...enums import TickType, ExchangeType

        with patch('os.environ'), patch('ccxt.gemini'):
            ec = ExchangeConfig()
            ec.exchange_type = ExchangeType.GEMINI
            e = GeminiExchange(ExchangeType.GEMINI, ec)
            e._running = True
            assert e

            e.ws = MagicMock()

            with patch('json.loads') as m1:
                for i, val in enumerate([TickType.TRADE,
                                         TickType.OPEN,
                                         TickType.FILL,
                                         TickType.CANCEL,
                                         TickType.CHANGE,
                                         TickType.ERROR]):
                    m1.return_value = {'events': [{"type": "accepted",
                                                   "order_id": "372456298",
                                                   "event_id": "372456299",
                                                   "client_order_id": "20170208_example",
                                                   "api_session": "AeRLptFXoYEqLaNiRwv8",
                                                   "symbol": "btcusd",
                                                   "side": "buy",
                                                   "order_type": "exchange limit",
                                                   "timestamp": "1478203017",
                                                   "timestampms": 1478203017455,
                                                   "is_live": True,
                                                   "is_cancelled": False,
                                                   "is_hidden": False,
                                                   "avg_execution_price": "0",
                                                   "original_amount": "14.0296",
                                                   "price": "1059.54"
                                                   }]}
                    e.receive()
