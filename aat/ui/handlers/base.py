import tornado.ioloop
import tornado.web
import tornado.websocket
from concurrent.futures import ThreadPoolExecutor
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from ...logging import log

class HTTPHandler(tornado.web.RequestHandler):
    '''Just a default handler'''
    executor = ThreadPoolExecutor(16)

    def get_current_user(self):
        return self.get_secure_cookie("token")

    def initialize(self, basepath='', wspath='', template='', template_dirs=None, *args, **kwargs):
        '''Initialize the server competition registry handler

        This handler is responsible for managing competition
        registration.

        Arguments:
            competitions {dict} -- a reference to the server's dictionary of competitions
        '''
        super(HTTPHandler, self).initialize(*args, **kwargs)
        self.basepath = basepath
        self.wspath = wspath
        self.template = template
        self.template_dirs = template_dirs or []

    def render_template(self, template, **kwargs):
        if hasattr(self, 'template_dirs'):
            template_dirs = self.template_dirs
        else:
            template_dirs = []

        if self.settings.get('template_path', ''):
            template_dirs.append(
                self.settings["template_path"]
            )
        env = Environment(loader=FileSystemLoader(template_dirs))

        try:
            template = env.get_template(self.template)
        except TemplateNotFound:
            raise TemplateNotFound(self.template)

        kwargs['current_user'] = self.current_user if self.current_user else ''
        kwargs['basepath'] = self.basepath
        kwargs['wspath'] = self.wspath
        content = template.render(**kwargs)
        return content

    def _set_400(self, log_message, *args):
        log.info(log_message, *args)
        self.set_status(400)
        self.finish('{"error":"400"}')
        raise tornado.web.HTTPError(400)

    def _set_401(self, log_message, *args):
        log.info(log_message, *args)
        self.set_status(401)
        self.finish('{"error":"401"}')
        raise tornado.web.HTTPError(401)

    def _set_403(self, log_message, *args):
        log.info(log_message, *args)
        self.set_status(403)
        self.finish('{"error":"403"}')
        raise tornado.web.HTTPError(403)
