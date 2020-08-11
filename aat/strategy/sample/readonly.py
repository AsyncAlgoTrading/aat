from aat import Strategy, Event
from pprint import pprint


class ReadOnlyStrategy(Strategy):
    def __init__(self, *args, **kwargs) -> None:
        super(ReadOnlyStrategy, self).__init__(*args, **kwargs)

    async def onStart(self, event: Event) -> None:
        pprint(self.instruments())

    async def onTrade(self, event: Event) -> None:
        pprint(event)

    async def onOrder(self, event):
        pprint(event)

    async def onExit(self, event: Event) -> None:
        print('Finishing...')
