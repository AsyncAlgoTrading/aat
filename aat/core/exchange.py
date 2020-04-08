# from ..binding import Exchange


class Exchange(object):
    def __init__(self, name):
        self._name = name

    def __repr__(self):
        return self._name
