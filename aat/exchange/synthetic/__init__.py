from ..exchange import Exchange


class SyntheticExchange(Exchange):
    def __init__(self, trading_engine):
        pass

    async def connect(self):
        pass

    async def tick(self):
        pass


Exchange.registerExchange('synthetic', SyntheticExchange)
