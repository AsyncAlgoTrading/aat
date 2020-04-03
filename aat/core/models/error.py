from pydantic import BaseModel
from typing import Any
from ...config import EventType


class Error(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    type: EventType = EventType.ERROR

    target: Any
    exception: BaseException
    handler: Any = None
