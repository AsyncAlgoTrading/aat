from typing import Any

from aat.common import _in_cpp

try:
    from aat.binding import ExchangeTypeCpp  # type: ignore

    _CPP = _in_cpp()
except ImportError:
    ExchangeTypeCpp = object
    _CPP = False


def _make_cpp_exchangetype(*args: Any, **kwargs: Any) -> ExchangeTypeCpp:
    return ExchangeTypeCpp(*args, **kwargs)
