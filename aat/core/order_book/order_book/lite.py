from typing import Callable, List, Mapping, Optional

from aat.core import Order, Instrument
from aat.config import Side, OrderType

from ..price_level import PriceLevelRO, _PriceLevel
from .order_book import OrderBook


class OrderBookLite(OrderBook):
    """A partial order book for clients of exchanges that don't
    provide order events but provide snapshots or overall state.

    This order book is composed of price levels with the volume
    simulated with a single, flag-less limit order.

    Args:
        instrument (Instrument): the instrument for the book
        exchange_name (str): name of the exchange
        callback (Function): callback on events
    """

    def __init__(
        self,
        instrument: Instrument,
        exchange_name: str = "",
        callback: Optional[Callable] = None,
    ):
        super().__init__(
            instrument=instrument, exchange_name=exchange_name, callback=callback
        )

    @staticmethod
    def fromPriceLevels(
        instrument: Instrument,
        exchange_name: str = "",
        callback: Optional[Callable] = None,
        price_levels: Optional[Mapping[Side, List[PriceLevelRO]]] = None,
    ) -> "OrderBookLite":
        """construct order book from price levels"""
        price_levels = price_levels or {}
        obl = OrderBookLite(instrument, exchange_name, callback)

        # create one order per price level
        for level in price_levels[Side.SELL]:
            level = level if isinstance(level, PriceLevelRO) else PriceLevelRO(level[0], level[1], 1)  # type: ignore
            obl.add(
                Order(
                    level.volume,
                    level.price,
                    Side.SELL,
                    obl.instrument,
                    obl.exchange,
                    order_type=OrderType.LIMIT,
                )
            )

        # create one order per price level
        for level in price_levels[Side.BUY]:
            level = level if isinstance(level, PriceLevelRO) else PriceLevelRO(level[0], level[1], 1)  # type: ignore
            obl.add(
                Order(
                    level.volume,
                    level.price,
                    Side.BUY,
                    obl.instrument,
                    obl.exchange,
                    order_type=OrderType.LIMIT,
                )
            )

        # return newly constructed order book
        return obl

    @staticmethod
    def fromOrderBook(ob: OrderBook) -> "OrderBookLite":
        # TODO
        raise NotImplementedError()

    def clone(self) -> "OrderBookLite":
        """clone an order book. useful when you want to do experiments on an orderbook without destroying it"""
        obl = OrderBookLite(self.instrument, self.exchange.name, self.callback)

        # create one order per price level
        for level in self._sell_levels:
            pl: _PriceLevel = self._sells[level]
            self.add(
                Order(
                    pl.volume,
                    pl.price,
                    Side.SELL,
                    self.instrument,
                    self.exchange,
                    order_type=OrderType.LIMIT,
                )
            )

        # create one order per price level
        for level in self._buy_levels:
            pl = self._buys[level]
            self.add(
                Order(
                    pl.volume,
                    pl.price,
                    Side.BUY,
                    self.instrument,
                    self.exchange,
                    order_type=OrderType.LIMIT,
                )
            )

        # return newly constructed order book
        return obl
