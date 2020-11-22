from aat import Strategy, Event, Order, OrderType, Side


class TestCancelAll(Strategy):
    def __init__(self, *args, **kwargs) -> None:
        super(TestCancelAll, self).__init__(*args, **kwargs)
        self._count = 0

    async def onTrade(self, event: Event) -> None:
        if self._count < 5:
            await self.newOrder(
                Order(
                    1,
                    10000000,
                    Side.SELL,
                    self.instruments()[0],
                    order_type=OrderType.LIMIT,
                )
            )
            self._count += 1
            assert len(self.orders()) == self._count
        else:
            await self.cancelAll()
            assert len(self.orders()) == 0


if __name__ == "__main__":
    from aat import TradingEngine, parseConfig

    cfg = parseConfig(
        [
            "--trading_type",
            "backtest",
            "--exchanges",
            "aat.exchange:SyntheticExchange,1,1000",
            "--strategies",
            "aat.tests.strategy.test_strategies.test_cancel_all::TestCancelAll",
        ]
    )
    print(cfg)
    t = TradingEngine(**cfg)
    t.start()
