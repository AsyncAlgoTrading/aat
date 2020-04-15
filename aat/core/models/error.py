from pydantic import BaseModel
from traceback import format_exception
from typing import Any
from ...config import EventType


class Error(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    type: EventType = EventType.ERROR

    target: Any
    exception: BaseException
    handler: Any = None

    def __str__(self):
        return '{}-{}\n{}'.format(self.handler, self.target, format_exception(type(self.exception), self.exception, self.exception.__traceback__))
