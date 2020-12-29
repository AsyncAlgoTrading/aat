from abc import ABCMeta
from typing import List, AsyncIterator

from aat import Instrument, Event


class _MarketData(metaclass=ABCMeta):
    """internal only class to represent the streaming-source
    side of a data source"""

    async def instruments(self) -> List[Instrument]:
        """get list of available instruments"""
        return []

    async def subscribe(self, instrument: Instrument) -> None:
        """subscribe to market data for a given instrument"""

    async def tick(self) -> AsyncIterator[Event]:
        """return data from exchange"""
