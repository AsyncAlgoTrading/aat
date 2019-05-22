import tornado.web
import os.path
from ....ui.handlers.base import HTTPHandler
from mock import MagicMock


class TestBase:
    def setup(self):
        settings = {
                "debug": "True",
                "template_path": os.path.join(os.path.dirname(__file__), '../', '../', '../', 'ui', 'assets', 'templates'),
                }
        self.app = tornado.web.Application(**settings)
        self.app._transforms = []

    def test_validate(self):
        req = MagicMock()
        req.body = ''
        x = HTTPHandler(self.app, req)
        x._transforms = []
        x.render_template('404.html')
