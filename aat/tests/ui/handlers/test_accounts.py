from ....ui.handlers.accounts import AccountsHandler
from .common import generateTornadoApplication
from mock import MagicMock, patch


class TestAccounts:
    def setup(self):
        self.app, self.login_code = generateTornadoApplication()

    def test_AccountsHandler(self):
        req = MagicMock()
        req.body = ''
        x = AccountsHandler(self.app, req, trading_engine=MagicMock(), psp_kwargs={})

        x.te.exchanges = MagicMock()
        x.te.exchanges.return_value.values.return_value = [MagicMock()]
        x.te.exchanges.return_value.values.return_value[0].accounts.return_value = [MagicMock()]
        x.te.exchanges.return_value.values.return_value[0].accounts.return_value[0].to_dict.return_value = {'test': 1}

        x._transforms = []
        with patch.object(x, 'get_secure_cookie') as mget:
            mget.return_value = self.login_code
            x.get()
