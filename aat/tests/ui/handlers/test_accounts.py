import tornado.web
import os.path
from ....ui.handlers.accounts import ServerAccountsHandler
from mock import MagicMock


class TestAccounts:
    def setup(self):
        settings = {
                "debug": "True",
                "template_path": os.path.join(os.path.dirname(__file__), '../', '../', '../', 'ui', 'assets', 'templates'),
                }

        self.app = tornado.web.Application(**settings)
        self.app._transforms = []

    def test_AccountsHandler(self):
        req = MagicMock()
        req.body = ''
        x = ServerAccountsHandler(self.app, req, trading_engine=MagicMock(), psp_kwargs={})
        x.te._ex.accounts = MagicMock()
        x.te._ex.accounts.return_value = [MagicMock()]
        x.te._ex.accounts.return_value[0].to_dict = MagicMock()
        x.te._ex.accounts.return_value[0].to_dict.return_value = {'test': 1}

        x._transforms = []
        x.get()

        assert len(x._write_buffer) > 0
