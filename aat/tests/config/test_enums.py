
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
