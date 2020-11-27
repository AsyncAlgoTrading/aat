from ...common import _in_cpp

try:
    from aat.binding import PositionCpp, CashPositionCpp, AccountCpp  # type: ignore

    _CPP = _in_cpp()

except ImportError:
    _CPP = False


def _make_cpp_position(*args, **kwargs):
    return PositionCpp(*args, **kwargs)


def _make_cpp_cash(*args, **kwargs):
    return CashPositionCpp(*args, **kwargs)


def _make_cpp_account(*args, **kwargs):
    return AccountCpp(*args, **kwargs)
