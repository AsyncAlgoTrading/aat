import time
import ujson
import base64
import hmac
import hashlib
import uuid
import secrets
import string
import os
import tornado.web
from ....trading import TradingEngine
from ....parser import parse_command_line_config


def generateApplication():
    config = parse_command_line_config(['--config=./config/sythetic.cfg'])

    # Instantiate trading engine
    #
    # The engine is responsible for managing the different components,
    # including the strategies, the bank/risk engine, and the
    # exchange/backtest engine.

    te = TradingEngine(config)

    # Run the live trading engine
    te.run()


def generateTornadoApplication():
    nonce = int(time.time() * 1000)
    encoded_payload = ujson.dumps({"nonce": nonce}).encode()
    b64 = base64.b64encode(encoded_payload)
    cookie_secret = hmac.new(str(uuid.uuid1()).encode(), b64, hashlib.sha384).hexdigest()
    login_code = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(20))

    settings = {
        "debug": "True",
        "template_path": os.path.join(os.path.dirname(__file__), '../', '../', '../', 'ui', 'assets', 'templates'),
        "cookie_secret": cookie_secret,
        "login_code": login_code
        }

    app = tornado.web.Application(**settings)
    app._transforms = []
    return app, login_code
