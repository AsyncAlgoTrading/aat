from ...common import _in_cpp

try:
    from ...binding import ExchangeTypeCpp  # type: ignore

    _CPP = _in_cpp()
except ImportError:
    _CPP = False


class ExchangeType(object):
    __slots__ = ["__name"]

    def __new__(cls, *args, **kwargs):
        if _CPP:
            return ExchangeTypeCpp(*args, **kwargs)
        return super(ExchangeType, cls).__new__(cls)

    def __init__(self, name):
        assert isinstance(name, str)
        self.__name = name

    # ******** #
    # Readonly #
    # ******** #
    @property
    def name(self) -> str:
        return self.__name

    def __eq__(self, other) -> bool:
        return self.name == other.name

    def __bool__(self) -> bool:
        return bool(self.__name)

    def __hash__(self):
        return hash(str(self))

    def toJson(self):
        return {"name": self.name}

    @staticmethod
    def fromJson(jsn):
        return ExchangeType(name=jsn["name"])

    def __repr__(self) -> str:
        return "Exchange({})".format(self.__name) if self.__name else "No Exchange"
