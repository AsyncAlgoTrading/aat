from typing import Any, List

from aat.common import _in_cpp

try:
    from ...binding import InstrumentCpp  # type: ignore

    _CPP = _in_cpp()
except ImportError:
    InstrumentCpp = object
    _CPP = False


def _make_cpp_instrument(*args: Any, **kwargs: Any) -> InstrumentCpp:
    if kwargs:
        full_args: List[Any] = list(args)
        full_args.append(kwargs.get("name"))
        full_args.append(kwargs.get("type"))
        args = tuple(full_args)
    return InstrumentCpp(*args)
