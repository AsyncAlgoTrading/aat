from pprint import pprint
from typing import Any
from aat import Strategy, Event, Instrument, InstrumentType, ExchangeType


class ReadOnlyStrategy(Strategy):
    def __init__(self, symbol: str, *args: Any, **kwargs: Any) -> None:
        super(ReadOnlyStrategy, self).__init__(*args, **kwargs)
        self._inst = Instrument(
            name=symbol, type=InstrumentType.EQUITY, exchange=ExchangeType("iex")
        )

    async def onStart(self, event: Event) -> None:
        await self.subscribe(self._inst)

    async def onTrade(self, event: Event) -> None:
        pprint(event)

    async def onOrder(self, event: Event) -> None:
        pprint(event)

    async def onExit(self, event: Event) -> None:
        print("Finishing...")


if __name__ == "__main__":
    from aat import TradingEngine, parseConfig

    cfg = parseConfig(
        [
            "--trading_type",
            "backtest",
            "--exchanges",
            "aat.exchange.public.iex:IEX,Tpk_ecc89ddf30a611e9958142010a80043c,True,1m,,,,",
            "--strategies",
            "aat.strategy.sample.iex.readonly:ReadOnlyStrategy,F",
        ]
    )
    print(cfg)
    t = TradingEngine(**cfg)
    t.start()
