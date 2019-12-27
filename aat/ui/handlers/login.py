import tornado
from .base import HTTPHandler
from ...logging import log


class LoginHandler(HTTPHandler):
    def get(self):
        '''Get the login page'''
        if self.current_user:
            self.redirect('/')
        else:
            log.critical(f'\n**********\nLogin code: {self.application.settings["login_code"]}\n**********')

            user = self.get_argument('code', '')
            if user == self.application.settings['login_code']:
                self.set_secure_cookie("token", user)
            else:
                self.redirect('/login')  # 404 in raw AAT

    def post(self):
        '''Login'''
        user = self.get_argument('code', '')
        if user == self.application.settings['login_code']:
            self.set_secure_cookie("token", user)
            self.redirect('/')
        else:
            self.redirect('/login')  # 404 in raw AAT


class LogoutHandler(HTTPHandler):
    @tornado.web.authenticated
    def get(self):
        '''Get the logout page'''
        if not self.current_user:
            self.redirect('/login')
        else:
            self.redirect('/logout')  # 404 in raw AAT

    def post(self):
        self.clear_cookie("user")
        self.redirect('/')
