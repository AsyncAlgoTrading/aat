from mock import patch, MagicMock


class TestExchange:
    def test_init(self):
        from ...config import ExchangeConfig
        from ...exchanges.coinbase import CoinbaseExchange
        from ...enums import ExchangeType

        ec = ExchangeConfig()
        ec.exchange_type = ExchangeType.COINBASE
        e = CoinbaseExchange(ExchangeType.COINBASE, ec)
        e._running = True
        assert e

    def test_receive(self):
        from ...config import ExchangeConfig
        from ...exchanges.coinbase import CoinbaseExchange
        from ...enums import TickType, ExchangeType

        with patch('os.environ'), patch('ccxt.coinbasepro'):
            ec = ExchangeConfig()
            ec.exchange_type = ExchangeType.COINBASE
            e = CoinbaseExchange(ExchangeType.COINBASE, ec)
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
                    m1.return_value = {'type': val,
                                       'sequence': i,
                                       'time': '2017-02-19T18:52:17.088000Z',
                                       'product_id': 'BTCUSD'}
                    e.receive()

    # def test_seqnum_fix(self):
    #     from ...lib.config import ExchangeConfig
    #     from ...lib.exchanges.gdax import GDAXExchange
    #     from ...lib.enums import TickType, ExchangeType

    #     with patch('os.environ'), patch('gdax.AuthenticatedClient'):
    #         ec = ExchangeConfig()
    #         ec.exchange_type = ExchangeType.GDAX
    #         e = GDAXExchange(ec)
    #         e._running = True
    #         assert e

    #         e.ws = MagicMock()

    #         with patch('json.loads') as m1:
    #             m1.return_value = {'type': TickType.TRADE,
    #                                'sequence': 0,
    #                                'time': '2017-02-19T18:52:17.088000Z',
    #                                'product_id': 'BTCUSD'}
    #             e.receive()
    #             for i, val in enumerate([TickType.TRADE,
    #                                      TickType.RECEIVED,
    #                                      TickType.OPEN,
    #                                      TickType.DONE,
    #                                      TickType.CHANGE,
    #                                      TickType.ERROR]):
    #                 m1.return_value = {'type': val,
    #                                    'sequence': 6-i,
    #                                    'time': '2017-02-19T18:52:17.088000Z',
    #                                    'product_id': 'BTCUSD'}
    #                 if i != 0:
    #                     assert e._missingseqnum
    #                 e.receive()
    #             assert e._missingseqnum == set()

    def test_trade_req_to_params_coinbase(self):
        from ...config import ExchangeConfig
        from ...exchanges.coinbase import CoinbaseExchange
        from ...enums import PairType, OrderType, OrderSubType, ExchangeType
        from ...structs import Instrument

        ec = ExchangeConfig()
        ec.exchange_type = ExchangeType.COINBASE
        e = CoinbaseExchange(ExchangeType.COINBASE, ec)

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
        assert(res1['product_id'] == 'BTC-USD')
        assert(res1['type'] == 'limit')
        assert(res1['post_only'] == '1')
        assert(res2['time_in_force'] == 'FOK')

    def test_CoinbaseHelpers_strToTradeType(self):
        from ...exchanges.coinbase import CoinbaseExchange
        from ...enums import TickType
        from ...config import ExchangeConfig
        from ...enums import ExchangeType
        ec = ExchangeConfig()
        ec.exchange_type = ExchangeType.COINBASE
        e = CoinbaseExchange(ExchangeType.COINBASE, ec)

        assert e.strToTradeType('match') == TickType.TRADE
        assert e.strToTradeType('received') == TickType.RECEIVED
        assert e.strToTradeType('open') == TickType.OPEN
        assert e.strToTradeType('done') == TickType.DONE
        assert e.strToTradeType('change') == TickType.CHANGE
        assert e.strToTradeType('heartbeat') == TickType.HEARTBEAT
        assert e.strToTradeType('flarg') == TickType.ERROR

    def test_CoinbaseHelpers_currencyToString(self):
        from ...exchanges.coinbase import CoinbaseExchange
        from ...enums import CurrencyType
        from ...config import ExchangeConfig
        from ...enums import ExchangeType
        ec = ExchangeConfig()
        ec.exchange_type = ExchangeType.COINBASE
        e = CoinbaseExchange(ExchangeType.COINBASE, ec)

        assert e.currencyToString(CurrencyType.BTC) == 'BTC'
        assert e.currencyToString(CurrencyType.ETH) == 'ETH'
        assert e.currencyToString(CurrencyType.LTC) == 'LTC'
        assert e.currencyToString(CurrencyType.BCH) == 'BCH'

    def test_CoinbaseHelpers_currencyPairToString(self):
        from ...exchanges.coinbase import CoinbaseExchange
        from ...enums import PairType
        from ...config import ExchangeConfig
        from ...enums import ExchangeType
        ec = ExchangeConfig()
        ec.exchange_type = ExchangeType.COINBASE
        e = CoinbaseExchange(ExchangeType.COINBASE, ec)

        assert e.currencyPairToString(PairType.BTCUSD) == 'BTC-USD'
        assert e.currencyPairToString(PairType.BTCETH) == 'BTC-ETH'
        assert e.currencyPairToString(PairType.BTCLTC) == 'BTC-LTC'
        assert e.currencyPairToString(PairType.BTCBCH) == 'BTC-BCH'
        assert e.currencyPairToString(PairType.ETHUSD) == 'ETH-USD'
        assert e.currencyPairToString(PairType.LTCUSD) == 'LTC-USD'
        assert e.currencyPairToString(PairType.BCHUSD) == 'BCH-USD'
        assert e.currencyPairToString(PairType.ETHBTC) == 'ETH-BTC'
        assert e.currencyPairToString(PairType.LTCBTC) == 'LTC-BTC'
        assert e.currencyPairToString(PairType.BCHBTC) == 'BCH-BTC'
