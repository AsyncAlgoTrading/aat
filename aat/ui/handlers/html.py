import tornado.web
from .base import HTTPHandler


class HTMLOpenHandler(HTTPHandler):
    def initialize(self, template=None, template_kwargs=None, **kwargs):
        super(HTMLOpenHandler, self).initialize()
        self.template = template
        self.template_kwargs = template_kwargs or {}

    def get(self, *args):
        '''Get the login page'''
        if not self.template:
            self.redirect('/')
        else:
            if self.request.path == '/logout':
                self.clear_cookie("user")
            template = self.render_template(self.template, **self.template_kwargs)
            self.write(template)


class HTMLHandler(HTMLOpenHandler):
    @tornado.web.authenticated
    def get(self, *args):
        '''Get the login page'''
        if not self.template:
            self.redirect('/')
        else:
            template = self.render_template(self.template, **self.template_kwargs)
            self.write(template)
