from aat.common import _in_cpp


try:
    from ...binding import InstrumentCpp  # type: ignore

    _CPP = _in_cpp()
except ImportError:
    _CPP = False


def _make_cpp_instrument(*args, **kwargs):
    return InstrumentCpp(*args, **kwargs)
