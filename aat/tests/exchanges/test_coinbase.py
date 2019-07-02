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
                                         TickType.OPEN,
                                         TickType.FILL,
                                         TickType.CANCEL,
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
