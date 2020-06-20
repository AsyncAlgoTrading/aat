from ...config import Side
from ..instrument import Instrument
from ..exchange import ExchangeType


class RiskManager(object):
    def __init__(self):
        pass

    def positions(self, instrument: Instrument = None, exchange: ExchangeType = None, side: Side = None):
        return "positions"

    def risk(self, position=None):
        return "risk"
