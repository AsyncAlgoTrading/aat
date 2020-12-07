import os
from typing import List, AsyncGenerator, Any

from aat.core import ExchangeType, Order, Instrument, Position, Event
from aat.config import TradingType, InstrumentType
from aat.exchange import Exchange

from .client import CoinbaseExchangeClient


class CoinbaseProExchange(Exchange):
    """Coinbase Pro Exchange"""

    def __init__(
        self,
        trading_type: TradingType,
        verbose: bool,
        api_key: str = "",
        api_secret: str = "",
        api_passphrase: str = "",
        **kwargs: dict
    ) -> None:
        self._trading_type = trading_type
        self._verbose = verbose

        # coinbase keys
        self._api_key = api_key or os.environ.get("API_KEY", "")
        self._api_secret = api_secret or os.environ.get("API_SECRET", "")
        self._api_passphrase = api_passphrase or os.environ.get("API_PASSPHRASE", "")

        # enforce authentication, otherwise we don't get enough
        # data to be interesting
        if not (self._api_key and self._api_secret and self._api_passphrase):
            raise Exception("No coinbase auth!")

        # don't implement backtest for now
        if trading_type == TradingType.BACKTEST:
            raise NotImplementedError()

        if self._trading_type == TradingType.SANDBOX:
            # Coinbase sandbox
            super().__init__(ExchangeType("coinbaseprosandbox"))
        else:
            # Coinbase Live trading
            print("*" * 100)
            print("*" * 100)
            print("WARNING: LIVE TRADING")
            print("*" * 100)
            print("*" * 100)
            super().__init__(ExchangeType("coinbasepro"))

        # Create an exchange client based on the coinbase docs
        # Note: cbpro doesnt seem to work as well as I remember,
        # and ccxt has moved to a "freemium" model where coinbase
        # pro now costs money for full access, so here i will just
        # implement the api myself.
        self._client = CoinbaseExchangeClient(
            self._trading_type,
            self.exchange(),
            self._api_key,
            self._api_secret,
            self._api_passphrase,
        )

        # list of market data subscriptions
        self._subscriptions: List[Instrument] = []

    # *************** #
    # General methods #
    # *************** #
    async def connect(self) -> None:
        """connect to exchange. should be asynchronous."""
        # instantiate instruments
        self._client.instruments()

    async def lookup(self, instrument: Instrument) -> List[Instrument]:
        """lookup an instrument on the exchange"""
        # TODO
        raise NotImplementedError()

    # ******************* #
    # Market Data Methods #
    # ******************* #
    async def tick(self) -> AsyncGenerator[Any, Event]:  # type: ignore[override]
        """return data from exchange"""

        # First, roll through order book snapshot
        async for item in self._client.orderBook(self._subscriptions):
            yield item

        # then stream in live updates
        async for tick in self._client.websocket(self._subscriptions):
            yield tick

    async def subscribe(self, instrument: Instrument) -> None:
        # can only subscribe to pair data
        if instrument.type == InstrumentType.PAIR:
            self._subscriptions.append(instrument)

    # ******************* #
    # Order Entry Methods #
    # ******************* #
    async def accounts(self) -> List[Position]:
        """get accounts from source"""
        return await self._client.accounts()

    async def newOrder(self, order: Order) -> bool:
        """submit a new order to the exchange. should set the given order's `id` field to exchange-assigned id"""
        return await self._client.newOrder(order)

    async def cancelOrder(self, order: Order) -> bool:
        """cancel a previously submitted order to the exchange."""
        return await self._client.cancelOrder(order)


Exchange.registerExchange("coinbase", CoinbaseProExchange)
