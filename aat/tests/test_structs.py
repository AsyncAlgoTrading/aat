from datetime import datetime


class TestStructs:
    def setup(self):
        pass
        # setup() before each test method

    def teardown(self):
        pass
        # teardown() after each test method

    @classmethod
    def setup_class(cls):
        pass
        # setup_class() before any methods in this class

    @classmethod
    def teardown_class(cls):
        pass
        # teardown_class() after any methods in this class

    def test_to_dict(self):
        from ..structs import Instrument
        from ..enums import PairType, InstrumentType
        i = Instrument(underlying=PairType.BTCUSD)
        x = i.to_dict()
        print(x)
        assert x == {'type': InstrumentType.PAIR, 'underlying': PairType.BTCUSD}

        x = i.to_dict(True)
        assert x == {'type': 'InstrumentType.PAIR', 'underlying': 'BTC/USD'}

        x = i.to_dict(True, True)
        assert x == {'type': 'InstrumentType.PAIR', 'underlying': 'BTC/USD'}

    def test_MarketData(self):
        from ..structs import MarketData, Instrument
        from ..enums import TickType, Side, PairType, ExchangeType
        m = MarketData(time=datetime.now(),
                       volume=1.0,
                       price=1.0,
                       instrument=Instrument(underlying=PairType.BTCUSD),
                       type=TickType.TRADE,
                       exchange=ExchangeType.COINBASE,
                       side=Side.BUY)
        # TODO no fields yet
        assert m

    def test_TradeRequest(self):
        from ..structs import TradeRequest, Instrument
        from ..enums import Side, OrderType, PairType, ExchangeType
        t = TradeRequest(side=Side.BUY,
                         instrument=Instrument(underlying=PairType.BTCUSD),
                         order_type=OrderType.MARKET,
                         volume=1.0,
                         exchange=ExchangeType.COINBASE,
                         price=1.0,
                         time=datetime.now())
        assert t
        # side = Side
        # volume = float
        # price = float
        # exchange = ExchangeType
        # currency = CurrencyType
        # order_type = OrderType
        # order_sub_type = OrderSubType

    def test_TradeResponse(self):
        from ..structs import TradeRequest, TradeResponse, TradeResult, Instrument
        from ..enums import Side, OrderType, PairType, ExchangeType
        req = TradeRequest(side=Side.BUY,
                           order_type=OrderType.MARKET,
                           exchange=ExchangeType.COINBASE,
                           instrument=Instrument(underlying=PairType.BTCUSD),
                           volume=1.0,
                           price=1.0,
                           time=datetime.now())
        t = TradeResponse(request=req,
                          side=Side.BUY,
                          instrument=Instrument(underlying=PairType.BTCUSD),
                          volume=0.0,
                          price=0.0,
                          status=TradeResult.FILLED,
                          exchange=ExchangeType.COINBASE,
                          time=datetime.now(),
                          order_id='1')
        assert t
        # side = Side
        # volume = float
        # price = float
        # success = bool
