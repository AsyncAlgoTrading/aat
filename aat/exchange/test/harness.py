from datetime import datetime, timedelta
from typing import List, Any, AsyncGenerator, Optional
from aat import Strategy
from aat.config import EventType, InstrumentType, Side, TradingType
from aat.core import ExchangeType, Event, Instrument, Trade, Order
from aat.exchange import Exchange


class Harness(Exchange):
    """Test harness exchange

    This is a synthetic exchange that runs through a sequence of data objects and
    asserts some specific behavior in the strategies under test"""

    def __init__(self, trading_type: TradingType, verbose: bool) -> None:
        super().__init__(ExchangeType("testharness"))
        self._trading_type = trading_type
        self._verbose = verbose
        self._instrument = Instrument("Test.inst", InstrumentType.EQUITY)

        self._id = 0
        self._start = datetime.now() - timedelta(days=30)
        self._client_order: Optional[Order] = None

    async def instruments(self) -> List[Instrument]:
        """get list of available instruments"""
        return [self._instrument]

    async def connect(self) -> None:
        # No-op
        pass

    async def tick(self) -> AsyncGenerator[Any, Event]:  # type: ignore[override]
        now = self._start
        for i in range(1000):
            if self._client_order:
                self._client_order.filled = self._client_order.volume
                t = Trade(
                    self._client_order.volume,
                    i,
                    taker_order=self._client_order,
                    maker_orders=[],
                )
                t.taker_order.timestamp = now
                self._client_order = None
                yield Event(type=EventType.TRADE, target=t)
                continue

            o = Order(
                1,
                i,
                Side.BUY,
                self._instrument,
                self.exchange(),
                timestamp=now,
                filled=1,
            )
            t = Trade(1, i, o, [])
            yield Event(type=EventType.TRADE, target=t)
            now += timedelta(minutes=30)

    async def newOrder(self, order: Order) -> bool:
        order.id = str(self._id)
        self._id += 1
        self._client_order = order
        return True


class TestStrategy(Strategy):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(TestStrategy, self).__init__(*args, **kwargs)
        self._orders: List[Order] = []
        self._trades: List[Trade] = []

    async def onStart(self, event: Event) -> None:
        self.periodic(self.onPeriodic, second=0, minute=30)

    async def onTrade(self, event: Event) -> None:
        pass

    async def onTraded(self, event: Event) -> None:
        self._trades.append(event.target)  # type: ignore

    async def onPeriodic(self) -> None:
        o = Order(1, 1, Side.BUY, self.instruments()[0], ExchangeType("testharness"))
        _ = await self.newOrder(o)
        self._orders.append(o)

    async def onExit(self, event: Event) -> None:
        assert len(self._orders) == len(self._trades)
        assert len(self._trades) == 334
        assert self._trades[0].price == 2
        assert self._trades[1].price == 3
        assert self._trades[-1].price == 999


if __name__ == "__main__":
    from aat import TradingEngine, parseConfig

    cfg = parseConfig(
        [
            "--trading_type",
            "backtest",
            "--exchanges",
            "aat.exchange.test.harness:Harness",
            "--strategies",
            "aat.exchange.test.harness:TestStrategy",
        ]
    )
    print(cfg)
    t = TradingEngine(**cfg)
    t.start()
