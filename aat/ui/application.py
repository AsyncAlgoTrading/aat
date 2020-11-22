import logging
import tornado.web

# from tornado_sqlalchemy_login.handlers import LoginHandler, LogoutHandler, RegisterHandler, APIKeyHandler
# from tornado_sqlalchemy_login import SQLAlchemyLoginManagerOptions, SQLAlchemyLoginManager


class ServerApplication(tornado.web.Application):
    def __init__(
        self,
        basepath="/",
        wspath="/api/v1/ws",
        handlers=None,
        debug=True,
        cookie_secret=None,
        *args,
        **kwargs
    ):

        handlers = handlers or []

        logging.getLogger("tornado.access").disabled = False

        # SQLAlchemy Login Configuration
        # sqlalchemy_login_config = SQLAlchemyLoginManagerOptions(
        #     port=port,
        #     UserClass=User,
        #     APIKeyClass=APIKey,
        # )

        settings = {
            "cookie_secret": cookie_secret,
            "login_url": basepath + "login",
            "debug": debug,
        }

        settings.update(**kwargs)

        super(ServerApplication, self).__init__(handlers, **settings)
