class TestCallback:
    def setup(self):
        pass
        # setup() before each test method

    def teardown(self):
        pass
        # teardown() after each test method

    @classmethod
    def setup_class(cls):
        # setup_class() before any methods in this class
        pass

    @classmethod
    def teardown_class(cls):
        # teardown_class() after any methods in this class
        pass

    def test_null_callback(self):
        from ..callback import NullCallback

        nc = NullCallback()
        assert nc.onTrade(None) is None
        assert nc.onReceived(None) is None
        assert nc.onOpen(None) is None
        assert nc.onDone(None) is None
        assert nc.onChange(None) is None
        assert nc.onError(None) is None
        assert nc.onAnalyze(None) is None
        assert nc.onHalt(None) is None
        assert nc.onContinue(None) is None

    def test_print_callback(self):
        from ..callback import Print
        pc = Print(onError=False)
        assert pc.onError == False
        assert pc.onTrade('test-print_onTrade') == None
