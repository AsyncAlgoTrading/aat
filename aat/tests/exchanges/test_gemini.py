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
                                         TickType.RECEIVED,
                                         TickType.OPEN,
                                         TickType.DONE,
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

    def test_trade_req_to_params_gemini(self):
        from ...exchanges.gemini import GeminiExchange
        from ...enums import PairType, OrderType, OrderSubType
        from ...structs import Instrument
        from ...config import ExchangeConfig
        from ...enums import ExchangeType
        ec = ExchangeConfig()
        ec.exchange_type = ExchangeType.GEMINI
        e = GeminiExchange(ExchangeType.GEMINI, ec)

        class tmp:
            def __init__(self, a=True):
                self.price = 'test'
                self.volume = 'test'
                self.instrument = Instrument(underlying=PairType.BTCUSD)
                self.order_type = OrderType.LIMIT
                self.order_sub_type = OrderSubType.POST_ONLY if a \
                    else OrderSubType.FILL_OR_KILL

        res1 = e.tradeReqToParams(tmp())
        res2 = e.tradeReqToParams(tmp(False))

        assert(res1['price'] == 'test')
        assert(res1['size'] == 'test')
        assert(res1['product_id'] == 'BTCUSD')
        assert(res1['type'] == 'limit')
        assert(res1['post_only'] == '1')
        assert(res2['time_in_force'] == 'FOK')

    def test_GeminiHelpers_reasonToTradeType(self):
        from ...exchanges.gemini import GeminiExchange
        from ...enums import TickType
        from ...config import ExchangeConfig
        from ...enums import ExchangeType
        ec = ExchangeConfig()
        ec.exchange_type = ExchangeType.GEMINI
        e = GeminiExchange(ExchangeType.GEMINI, ec)

        assert e.reasonToTradeType('CANCEL') == TickType.DONE
        assert e.reasonToTradeType('PLACE') == TickType.OPEN
        assert e.reasonToTradeType('INITIAL') == TickType.OPEN

    def test_GeminiHelpers_strToTradeType(self):
        from ...exchanges.gemini import GeminiExchange
        from ...enums import TickType
        from ...config import ExchangeConfig
        from ...enums import ExchangeType
        ec = ExchangeConfig()
        ec.exchange_type = ExchangeType.GEMINI
        e = GeminiExchange(ExchangeType.GEMINI, ec)

        assert e.strToTradeType('trade') == TickType.TRADE
        assert e.strToTradeType('change') == TickType.CHANGE
        assert e.strToTradeType('heartbeat') == TickType.HEARTBEAT

    def test_GeminiHelpers_currencyPairToString(self):
        from ...exchanges.gemini import GeminiExchange
        from ...enums import PairType
        from ...config import ExchangeConfig
        from ...enums import ExchangeType
        ec = ExchangeConfig()
        ec.exchange_type = ExchangeType.GEMINI
        e = GeminiExchange(ExchangeType.GEMINI, ec)

        assert e.currencyPairToString(PairType.BTCUSD) == 'BTCUSD'
        assert e.currencyPairToString(PairType.ETHUSD) == 'ETHUSD'
        assert e.currencyPairToString(PairType.ZECUSD) == 'ZECUSD'
        assert e.currencyPairToString(PairType.ETHBTC) == 'ETHBTC'
        assert e.currencyPairToString(PairType.ZECETH) == 'ZECETH'
