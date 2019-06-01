from datetime import datetime


class TestUtils:
    def test_struct(self):
        from ..utils import struct

        @struct
        class Test:
            a = int
            b = str

        t = Test(a=5, b='')

        assert t.a == 5
        assert t.b == ''

    def test_parse_date(self):
        from datetime import datetime
        from ..utils import parse_date
        gold = datetime(2016, 11, 16, 0, 0)
        date1 = parse_date('1479272400.0')
        date2 = parse_date('2016-11-16T00:00:00.000000Z')
        print(gold)
        print(date1)
        print(date2)

        assert gold == date1 == date2

    def test_struct_warnings(self):
        from ..utils import struct

        @struct
        class Test:
            a = int, 5

        t = Test()

        try:
            print(t.a)
            assert False
        except:
            pass
        t.a = 5
        assert t.a == 5

    def test_ex_type_to_ex(self):
        from ..utils import ex_type_to_ex
        from ..enums import ExchangeType
        from ..exchanges.coinbase import CoinbaseExchange
        assert ex_type_to_ex(ExchangeType.COINBASE) == CoinbaseExchange

    def test_set_verbose(self):
        import logging
        from ..utils import set_verbose
        from ..logging import LOG as log, \
            STRAT as slog, \
            DATA as dlog, \
            RISK as rlog, \
            EXEC as exlog, \
            SLIP as sllog, \
            TXNS as tlog, \
            MANUAL as mlog, \
            ERROR as elog
        set_verbose(2)

        assert(log.level == logging.DEBUG)
        assert(slog.level == logging.DEBUG)
        assert(dlog.level == logging.DEBUG)
        assert(rlog.level == logging.DEBUG)
        assert(exlog.level == logging.DEBUG)
        assert(sllog.level == logging.DEBUG)
        assert(tlog.level == logging.DEBUG)
        assert(mlog.level == logging.DEBUG)
        assert(elog.level == logging.DEBUG)

    def test_get_keys_from_environment(self):
        from ..utils import get_keys_from_environment
        import os
        os.environ['TEST_API_KEY'] = 'test'
        os.environ['TEST_API_SECRET'] = 'test'
        os.environ['TEST_API_PASS'] = 'test'
        one, two, three = get_keys_from_environment('TEST')
        assert(one == 'test')
        assert(two == 'test')
        assert(three == 'test')

    def test_str_to_currency_type(self):
        from ..utils import str_to_currency_type
        from ..enums import CurrencyType
        assert(str_to_currency_type('BTC') == CurrencyType.BTC)
        assert(str_to_currency_type('ETH') == CurrencyType.ETH)
        assert(str_to_currency_type('LTC') == CurrencyType.LTC)
        assert(str_to_currency_type('USD') == CurrencyType.USD)
        assert(str_to_currency_type('ZRX') == CurrencyType.ZRX)

    def test_str_to_side(self):
        from ..utils import str_to_side
        from ..enums import Side
        assert(str_to_side('BUY') == Side.BUY)
        assert(str_to_side('SELL') == Side.SELL)
        assert(str_to_side('OTHER') == Side.NONE)

    def test_str_to_order_type(self):
        from ..utils import str_to_order_type
        from ..enums import OrderType
        assert(str_to_order_type('MARKET') == OrderType.MARKET)
        assert(str_to_order_type('LIMIT') == OrderType.LIMIT)
        assert(str_to_order_type('OTHER') == OrderType.NONE)

    def test_str_to_exchange(self):
        from ..utils import str_to_exchange
        from ..enums import ExchangeType
        assert(str_to_exchange('bitfinex') == ExchangeType.BITFINEX)
        assert(str_to_exchange('bitstamp') == ExchangeType.BITSTAMP)
        assert(str_to_exchange('gemini') == ExchangeType.GEMINI)
        assert(str_to_exchange('hitbtc') == ExchangeType.HITBTC)
        assert(str_to_exchange('itbit') == ExchangeType.ITBIT)
        assert(str_to_exchange('kraken') == ExchangeType.KRAKEN)
        assert(str_to_exchange('lake') == ExchangeType.LAKE)
        assert(str_to_exchange('coinbase') == ExchangeType.COINBASE)

    def test_str_to_currency_pair_type(self):
        from ..utils import str_to_currency_pair_type
        from ..enums import PairType, CurrencyType

        for c1, v1 in CurrencyType.__members__.items():
            for c2, v2 in CurrencyType.__members__.items():
                if c1 == c2 or \
                   c1 == 'USD' or \
                   c2 == 'USD' or \
                   c1 == 'NONE' or \
                   c2 == 'NONE':
                    continue
                assert str_to_currency_pair_type(c1 + '/' + c2) == PairType.from_string(c1 + '/' + c2)
                assert str_to_currency_pair_type(c1 + '-' + c2) == PairType.from_string(c1, c2)
                assert str_to_currency_pair_type(c1 + c2) == PairType.from_string(c1, c2)

    def test_trade_req_to_params(self):
        from ..utils import trade_req_to_params
        from ..structs import TradeRequest, Instrument, ExchangeType
        from ..enums import Side, OrderType, PairType

        t = TradeRequest(side=Side.BUY,
                         volume=1.0,
                         price=1.0,
                         instrument=Instrument(underlying=PairType.BTCUSD),
                         exchange=ExchangeType.COINBASE,
                         order_type=OrderType.LIMIT,
                         time=datetime.now())

        ret = trade_req_to_params(t)

        assert ret['symbol'] == 'BTC/USD'
        assert ret['side'] == 'buy'
        assert ret['type'] == 'limit'
        assert ret['amount'] == 1.0
        assert ret['price'] == 1.0
