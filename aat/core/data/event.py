from typing import Mapping, Union
from .cpp import _CPP, _make_cpp_event
from .data import Data
from .order import Order
from .trade import Trade
from .error import Error
from ...config import EventType


class Event(object):
    __slots__ = ["__type", "__target"]

    # for convenience
    Types = EventType

    def __new__(cls, *args, **kwargs):  # type: ignore
        if _CPP:
            return _make_cpp_event(*args, **kwargs)
        return super(Event, cls).__new__(cls)

    def __init__(
        self, type: EventType, target: Union[Data, Order, Trade, Error, None]
    ) -> None:
        self.__type = type
        self.__target = target

    # ******** #
    # Readonly #
    # ******** #
    @property
    def type(self) -> EventType:
        return self.__type

    @property
    def target(self) -> Union[Data, Order, Trade, Error, None]:
        return self.__target  # type: ignore
        # ignore None type so typing is happy in other parts

    def __repr__(self) -> str:
        return f"Event(type={self.type}, target={self.target})"

    def json(self, flat: bool = False) -> Mapping[str, Union[str, int, float, dict]]:
        if flat:
            # TODO
            raise NotImplementedError()
        target = (
            {
                "target." + k: v
                for k, v in (
                    self.target.json(flat=flat) if hasattr(self.target, "json") else {}
                ).items()
            }
            if self.target
            else {"target": ""}
        )

        ret = {"type": self.type.value}

        ret.update(target)
        return ret
