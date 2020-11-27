from aat.common import _in_cpp


try:
    from aat.binding import ExchangeTypeCpp  # type: ignore

    _CPP = _in_cpp()
except ImportError:
    _CPP = False


def _make_cpp_exchangetype(*args, **kwargs):
    return ExchangeTypeCpp(*args, **kwargs)
