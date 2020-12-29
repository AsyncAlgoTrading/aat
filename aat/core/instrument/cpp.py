from typing import Any

from aat.common import _in_cpp

try:
    from ...binding import InstrumentCpp  # type: ignore

    _CPP = _in_cpp()
except ImportError:
    InstrumentCpp = object
    _CPP = False


def _make_cpp_instrument(*args: Any, **kwargs: Any) -> InstrumentCpp:
    return InstrumentCpp(*args, **kwargs)
