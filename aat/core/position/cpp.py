from typing import Any
from ...common import _in_cpp

try:
    from aat.binding import PositionCpp, CashPositionCpp, AccountCpp  # type: ignore

    _CPP = _in_cpp()

except ImportError:
    _CPP = False


def _make_cpp_position(*args: Any, **kwargs: Any) -> PositionCpp:
    return PositionCpp(*args, **kwargs)


def _make_cpp_cash(*args: Any, **kwargs: Any) -> CashPositionCpp:
    return CashPositionCpp(*args, **kwargs)


def _make_cpp_account(*args: Any, **kwargs: Any) -> AccountCpp:
    return AccountCpp(*args, **kwargs)
