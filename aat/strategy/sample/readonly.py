from pprint import pprint
from typing import Any
from aat import Strategy, Event


class ReadOnlyStrategy(Strategy):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(ReadOnlyStrategy, self).__init__(*args, **kwargs)

    async def onStart(self, event: Event) -> None:
        pprint(self.instruments())
        pprint(self.positions())

        for i in self.instruments():
            print(i)
            await self.subscribe(i)

    async def onTrade(self, event: Event) -> None:
        pprint(event)

    async def onOrder(self, event: Event) -> None:
        pprint(event)

    async def onExit(self, event: Event) -> None:
        print("Finishing...")
