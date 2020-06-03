from ...config import InstrumentType
from ...common import _in_cpp

try:
    from ...binding import InstrumentCpp
    _CPP = _in_cpp()
except ImportError:
    _CPP = False




class Instrument(object):
    def __new__(cls, *args, **kwargs):
        if _CPP:
            return InstrumentCpp(*args, **kwargs)
        return super(Instrument, cls).__new__(cls)

    def __init__(self, name, type=InstrumentType.EQUITY):
        self._name = name
        self._type = type

    def __eq__(self, other):
        return self._name == other._name and self._type == other._type

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        return f'({self._name}-{self._type})'
