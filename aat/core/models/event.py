# from ...binding import Event


from pydantic import BaseModel
from typing import Any
from ...config import EventType


class Event(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    # timestamp: int
    type: EventType
    target: Any

    def __str__(self):
        return f'<{self.type}-{self.target}>'
