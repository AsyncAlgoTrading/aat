# from ..binding import ExchangeType


class ExchangeType(object):
    def __init__(self, name):
        self._name = name

    def __repr__(self):
        return self._name
