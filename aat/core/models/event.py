from typing import Mapping, Union
from ...config import EventType
from ...common import _in_cpp

try:
    from aat.binding import EventCpp
    _CPP = _in_cpp()
except ImportError:
    _CPP = False


class Event(object):
    __slots__ = [
        "__type",
        "__target",
    ]

    # for convenience
    Types = EventType

    def __new__(cls, *args, **kwargs):
        if _CPP:
            return EventCpp(*args, **kwargs)
        return super(Event, cls).__new__(cls)

    def __init__(self, type, target):
        self.__type = type
        self.__target = target

    # ******** #
    # Readonly #
    # ******** #
    @property
    def type(self):
        return self.__type

    @property
    def target(self):
        return self.__target

    def __repr__(self):
        return f'Event(type={self.type}, target={self.target})'

    def to_json(self) -> Mapping[str, Union[str, int, float]]:
        return \
            {'type': self.type.value,
             'target': self.target.to_json()}
