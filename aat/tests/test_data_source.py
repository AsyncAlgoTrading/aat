
class TestDataSource:
    def setup(self):
        pass

    def teardown(self):
        pass

    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def test_StreamingDataSource(self):
        from ..data_source import StreamingDataSource
        from ..callback import Callback
        from ..enums import TickType

        try:
            x = StreamingDataSource()
            assert False
        except:
            pass

        class Test(StreamingDataSource):
            def run(self, engine):
                pass

            def close(self):
                pass

            def receive(self):
                pass

            def seqnum(self, num):
                pass

            def tickToData(self):
                pass

        class TestCB(Callback):
            def onTrade(self):
                pass

            def onReceived(self):
                pass

            def onOpen(self):
                pass

            def onDone(self):
                pass

            def onChange(self):
                pass

            def onError(self):
                pass

            def onAnalyze(self):
                pass

            def onHalt(self, data):
                pass

            def onContinue(self, data):
                pass

        try:
            t = Test()

            t.registerCallback(TestCB())
            assert t._callbacks
            assert len(t._callbacks) == 9
            assert len(t._callbacks[TickType.ERROR]) == 1

        except:
            assert False
