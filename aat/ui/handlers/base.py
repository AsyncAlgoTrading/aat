import tornado.ioloop
import tornado.web
import tornado.websocket
from jinja2 import Environment, FileSystemLoader, TemplateNotFound


class HTTPHandler(tornado.web.RequestHandler):
    '''Just a default handler'''
    def initialize(self, *args, **kwargs):
        '''Initialize the server competition registry handler

        This handler is responsible for managing competition
        registration.

        Arguments:
            competitions {dict} -- a reference to the server's dictionary of competitions
        '''
        super(HTTPHandler, self).initialize(*args, **kwargs)

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
            template = env.get_template(template)
        except TemplateNotFound:
            raise TemplateNotFound(template)

        kwargs['current_user'] = self.current_user.decode('utf-8') if self.current_user else ''
        content = template.render(**kwargs)
        return content


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    '''Just a default handler'''
    def initialize(self, *args, **kwargs):
        '''Initialize the server competition registry handler

        This handler is responsible for managing competition
        registration.

        Arguments:
            competitions {dict} -- a reference to the server's dictionary of competitions
        '''
        super(WebSocketHandler, self).initialize(*args, **kwargs)
