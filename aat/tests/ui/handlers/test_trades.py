import tornado.web
import os.path
from ....ui.handlers.trades import TradesHandler
from mock import MagicMock
import tornado.websocket


class TestMessages:
    def setup(self):
        settings = {
                "debug": "True",
                "template_path": os.path.join(os.path.dirname(__file__), '../', '../', 'ui', 'assets', 'templates'),
                }
        self.app = tornado.web.Application(**settings)
        self.app._transforms = []

    def test_ServerMessagesMixin(self):
        req = MagicMock()
        req.body = ''

        x = TradesHandler(self.app, req, trading_engine=MagicMock(), psp_kwargs={})
        x._transforms = []

        x.te = MagicMock()
        x.te._ex = MagicMock()
        x.te._ex.messages = MagicMock()
        x.te._ex.messages.return_value = [MagicMock()]
        x.te._ex.messages.return_value[0].to_dict = MagicMock()
        x.te._ex.messages.return_value[0].to_dict.return_value = {'test': 1, 'instrument': {'underlying': 'test'}}

        x.get_data()
        x.get_data('test')
        x.get_data(None, 'BTCUSD')

        x.te._ex.messages.return_value = {'TRADE': [MagicMock()]}
        x.te._ex.messages.return_value['TRADE'][0].to_dict = MagicMock()
        x.te._ex.messages.return_value['TRADE'][0].to_dict.return_value = {'test': 1}

        x.get_data()
        x.get_data(pair='test')
        x.get_data(pair='BTCUSD')

    def test_ServerMessages(self):
        req = MagicMock()
        req.body = ''

        x = TradesHandler(self.app, req, trading_engine=MagicMock(), psp_kwargs={})
        x._transforms = []

        x.te._ex.messages = MagicMock()
        x.te._ex.messages.return_value = [MagicMock()]
        x.te._ex.messages.return_value[0].to_dict = MagicMock()
        x.te._ex.messages.return_value[0].to_dict.return_value = {'test': 1, 'instrument': {'underlying': 'test'}}
        x.get()
