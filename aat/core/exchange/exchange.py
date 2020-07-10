from ...common import _in_cpp

try:
    from ...binding import ExchangeTypeCpp
    _CPP = _in_cpp()
except ImportError:
    _CPP = False


class ExchangeType(object):
    def __new__(cls, *args, **kwargs):
        if _CPP:
            return ExchangeTypeCpp(*args, **kwargs)
        return super(ExchangeType, cls).__new__(cls)

    def __init__(self, name):
        self._name = name

    def __repr__(self):
        return self._name if self._name else "No Exchange"
