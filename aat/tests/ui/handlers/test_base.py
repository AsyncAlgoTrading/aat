from .common import generateTornadoApplication
from ....ui.handlers.base import HTTPHandler
from mock import MagicMock


class TestBase:
    def setup(self):
        self.app, self.login_code = generateTornadoApplication()

    def test_validate(self):
        req = MagicMock()
        req.body = ''
        x = HTTPHandler(self.app, req)
        x._transforms = []
        x.render_template('404.html')
