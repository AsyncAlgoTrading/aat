from typing import Any
from pprint import pprint

from aat import Strategy, Event, Order, Trade, Side, Instrument, InstrumentType


class BuyAndHoldCBStrategy(Strategy):
    def __init__(self, notional: str, *args: Any, **kwargs: Any) -> None:
        super(BuyAndHoldCBStrategy, self).__init__(*args, **kwargs)
        self._notional = float(notional)

    async def onStart(self, event: Event) -> None:
        pprint(self.instruments())
        pprint(self.positions())

        await self.subscribe(Instrument("BTC-USD", InstrumentType.PAIR))

    async def onTrade(self, event: Event) -> None:
        """Called whenever a `Trade` event is received"""
        # pprint(event)
        trade: Trade = event.target  # type: ignore

        # no past trades, no current orders
        if not self.orders(trade.instrument) and not self.trades(trade.instrument):
            req = Order(
                side=Side.BUY,
                price=trade.price,
                volume=self._notional / trade.price,
                instrument=trade.instrument,
                order_type=Order.Types.MARKET,
                exchange=trade.exchange,
            )

            print("requesting buy : {}".format(req))

            await self.newOrder(req)

    async def onBought(self, event: Event) -> None:
        trade: Trade = event.target  # type: ignore
        print("bought {:.2f} @ {:.2f}".format(trade.volume, trade.price))

    async def onRejected(self, event: Event) -> None:
        print("order rejected")
        import sys

        sys.exit(0)

    async def onExit(self, event: Event) -> None:
        print("Finishing...")


if __name__ == "__main__":
    from aat import TradingEngine, parseConfig

    cfg = parseConfig(
        [
            "--trading_type",
            "sandbox",
            "--load_accounts",
            "--exchanges",
            "aat.exchange.crypto.coinbase:CoinbaseProExchange,,,,l2",
            "--strategies",
            "aat.strategy.sample.coinbase.buy_and_hold:BuyAndHoldCBStrategy",
        ]
    )

    # OR via config file
    """
        [general]
        verbose=0
        trading_type=sandbox
        load_accounts=1

        [exchange]
        exchanges=
            aat.exchange.crypto.coinbase:CoinbaseProExchange

        [strategy]
        strategies =
            aat.strategy.sample.coinbase.buy_and_hold:BuyAndHoldCBStrategy,1000
    """

    print(cfg)
    t = TradingEngine(**cfg)
    t.start()
