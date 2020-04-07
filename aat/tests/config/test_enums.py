
class TestEnums:
    def test_side(self):
        from aat.binding import Side
        assert Side.BUY.name == "BUY"
        assert Side.SELL.name == "SELL"

    def test_event_type(self):
        from aat.binding import EventType
        assert EventType.TRADE.name == "TRADE"
        assert EventType.OPEN.name == "OPEN"
        assert EventType.CANCEL.name == "CANCEL"
        assert EventType.CHANGE.name == "CHANGE"
        assert EventType.FILL.name == "FILL"
        assert EventType.DATA.name == "DATA"
        assert EventType.HALT.name == "HALT"
        assert EventType.CONTINUE.name == "CONTINUE"
        assert EventType.ERROR.name == "ERROR"
        assert EventType.START.name == "START"
        assert EventType.EXIT.name == "EXIT"

    def test_data_type(self):
        from aat.binding import DataType
        assert DataType.ORDER.name == "ORDER"
        assert DataType.TRADE.name == "TRADE"

    def test_instrument_type(self):
        from aat.binding import InstrumentType
        assert InstrumentType.CURRENCY.name == "CURRENCY"
        assert InstrumentType.EQUITY.name == "EQUITY"

    def test_order_type(self):
        from aat.binding import OrderType
        assert OrderType.LIMIT.name == "LIMIT"
        assert OrderType.MARKET.name == "MARKET"
        assert OrderType.STOP.name == "STOP"

    def test_order_flag(self):
        from aat.binding import OrderFlag
        assert OrderFlag.NONE.name == "NONE"
        assert OrderFlag.FILL_OR_KILL.name == "FILL_OR_KILL"
        assert OrderFlag.ALL_OR_NONE.name == "ALL_OR_NONE"
        assert OrderFlag.IMMEDIATE_OR_CANCEL.name == "IMMEDIATE_OR_CANCEL"
