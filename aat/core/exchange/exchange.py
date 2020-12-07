from .cpp import _CPP, _make_cpp_exchangetype


class ExchangeType(object):
    __slots__ = ["__name"]

    def __new__(cls, *args, **kwargs):  # type: ignore
        if _CPP:
            return _make_cpp_exchangetype(*args, **kwargs)
        return super(ExchangeType, cls).__new__(cls)

    def __init__(self, name: str) -> None:
        assert isinstance(name, str)
        self.__name = name

    # ******** #
    # Readonly #
    # ******** #
    @property
    def name(self) -> str:
        return self.__name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ExchangeType):
            return False
        return self.name == other.name

    def __bool__(self) -> bool:
        return bool(self.__name)

    def __hash__(self) -> int:
        return hash(str(self))

    def json(self) -> dict:
        return {"name": self.name}

    @staticmethod
    def fromJson(jsn: dict) -> "ExchangeType":
        return ExchangeType(name=jsn["name"])

    def __repr__(self) -> str:
        return "Exchange({})".format(self.__name) if self.__name else "No Exchange"
