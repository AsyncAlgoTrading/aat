from .common import generateTornadoApplication
from ....ui.handlers.html import HTMLHandler, HTMLOpenHandler
from mock import MagicMock, patch
from tornado.web import HTTPError


class TestHTML:
    def setup(self):
        self.app, self.login_code = generateTornadoApplication()

    def test_HTMLOpenHandler(self):
        req = MagicMock()
        req.body = ''
        x = HTMLOpenHandler(self.app, req, template='404.html')
        x._transforms = []
        x.get_current_user = lambda: False

        x.template = '404.html'

        with patch.object(x, 'get_secure_cookie') as mget:
            mget.return_value = self.login_code
            x.get()

        x = HTMLOpenHandler(self.app, req, template=None)
        x._transforms = []
        x.get_current_user = lambda: False
        with patch.object(x, 'get_secure_cookie') as mget:
            mget.return_value = self.login_code
            x.get()

    def test_HTMLHandler(self):
        req = MagicMock()
        req.body = ''
        x = HTMLHandler(self.app, req, template='404.html')
        x._transforms = []
        x.get_current_user = lambda: False

        x.template = '404.html'
        try:
            with patch.object(x, 'get_secure_cookie') as mget:
                mget.return_value = self.login_code
                x.get()
            assert False
        except HTTPError:
            pass

        x = HTMLHandler(self.app, req, template=None)
        x._transforms = []
        x.get_current_user = lambda: True
        with patch.object(x, 'get_secure_cookie') as mget:
            mget.return_value = self.login_code
            x.get()

        x = HTMLHandler(self.app, req, template='404.html')
        x._transforms = []
        x.get_current_user = lambda: b'test'
        with patch.object(x, 'get_secure_cookie') as mget:
            mget.return_value = self.login_code
            x.get()
