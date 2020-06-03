from pydantic import BaseModel
from typing import Any
from ...config import EventType
from ...common import _in_cpp

try:
    from aat.binding import EventCpp
    _CPP = _in_cpp()
except ImportError:
    _CPP = False


class Event(BaseModel):
    def __new__(cls, *args, **kwargs):
        if _CPP:
            return EventCpp(*args, **kwargs)
        return super(Event, cls).__new__(cls)

    Types = EventType

    class Config:
        arbitrary_types_allowed = True

    # timestamp: int
    type: EventType
    target: Any

    def __str__(self):
        return f'<{self.type}-{self.target}>'
