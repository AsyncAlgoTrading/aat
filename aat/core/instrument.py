# from ..binding import Instrument
from ..config import InstrumentType


class Instrument(object):
    def __init__(self, name, type=InstrumentType.EQUITY):
        self._name = name
        self._type = type

    def __repr__(self):
        return f'({self._name}-{self._type})'
