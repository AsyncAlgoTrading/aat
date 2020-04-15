# from ..binding import Instrument
from ...config import InstrumentType


class Instrument(object):
    def __init__(self, name, type=InstrumentType.EQUITY):
        self._name = name
        self._type = type

    def __eq__(self, other):
        return self._name == other._name and self._type == other._type

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        return f'({self._name}-{self._type})'
