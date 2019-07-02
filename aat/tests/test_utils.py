from datetime import datetime


class TestUtils:
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

    def test_ex_type_to_ex(self):
        from ..utils import ex_type_to_ex
        from ..enums import ExchangeType
        from ..exchanges.coinbase import CoinbaseExchange
        assert ex_type_to_ex(ExchangeType.COINBASE) == CoinbaseExchange

    def test_set_verbose(self):
        import logging
        from ..utils import set_verbose
        from ..logging import log
        set_verbose(2)

        assert(log.level == logging.DEBUG)

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
        assert(str_to_exchange('coinbase') == ExchangeType.COINBASE)
        assert(str_to_exchange('gemini') == ExchangeType.GEMINI)
        assert(str_to_exchange('kraken') == ExchangeType.KRAKEN)
        assert(str_to_exchange('poloniex') == ExchangeType.POLONIEX)

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
