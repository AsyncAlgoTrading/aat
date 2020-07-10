from datetime import datetime
from traceback import format_exception
from ...config import DataType


class Error(object):
    __slots__ = [
        "__target",
        "__exception",
        "__handler",
        "__timestamp",
        "__type",
    ]

    def __init__(self, target, exception, handler):
        self.__timestamp = datetime.now()
        self.__type = DataType.ERROR
        self.__target = target
        self.__exception = exception
        self.__handler = handler

    # ******** #
    # Readonly #
    # ******** #
    @property
    def timestamp(self) -> int:
        return self.__timestamp

    @property
    def type(self):
        return self.__type

    @property
    def target(self):
        return self.__target

    @property
    def exception(self):
        return self.__exception

    @property
    def handler(self):
        return self.__handler

    def __repr__(self) -> str:
        return f'Error( timestamp={self.timestamp}, handler={self.handler}, exception={format_exception(type(self.exception), self.exception, self.exception.__traceback__)})'
