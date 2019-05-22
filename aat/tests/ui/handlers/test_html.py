import tornado.web
import os.path
from ....ui.handlers.html import HTMLHandler, HTMLOpenHandler
from mock import MagicMock
from tornado.web import HTTPError


class TestHTML:
    def setup(self):
        settings = {
                "debug": "True",
                "template_path": os.path.join(os.path.dirname(__file__), '../', '../', '../', 'ui', 'assets', 'templates'),
                }
        self.app = tornado.web.Application(**settings)
        self.app._transforms = []

    def test_HTMLOpenHandler(self):
        req = MagicMock()
        req.body = ''
        x = HTMLOpenHandler(self.app, req, template='404.html')
        x._transforms = []
        x.get_current_user = lambda: False

        x.template = '404.html'
        x.get()

        x = HTMLOpenHandler(self.app, req, template=None)
        x._transforms = []
        x.get_current_user = lambda: False
        x.get()

    def test_HTMLHandler(self):
        req = MagicMock()
        req.body = ''
        x = HTMLHandler(self.app, req, template='404.html')
        x._transforms = []
        x.get_current_user = lambda: False

        x.template = '404.html'
        try:
            x.get()
            assert False
        except HTTPError:
            pass

        x = HTMLHandler(self.app, req, template=None)
        x._transforms = []
        x.get_current_user = lambda: True
        x.get()

        x = HTMLHandler(self.app, req, template='404.html')
        x._transforms = []
        x.get_current_user = lambda: b'test'
        x.get()
