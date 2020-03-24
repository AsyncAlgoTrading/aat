import asyncio
from aiostream.stream import merge
from traitlets.config.application import Application
from traitlets import validate, TraitError, Unicode, Bool, List, Instance
from ..exchange import Exchange


class TradingEngine(Application):
    '''A configureable trading application'''
    name = 'AAT'
    description = 'async algorithmic trading engine'

    verbose = Bool(default_value=True)
    port = Unicode(default_value='8080', help="Port to run on").tag(config=True)
    trading_type = Unicode(default_value='simulation')
    exchanges = List(trait=Instance(klass=Exchange))
    event_loop = Instance(klass=asyncio.events.AbstractEventLoop)

    aliases = {
        'port': 'AAT.port',
        'trading_type': 'AAT.trading_type',
    }

    @validate('trading_type')
    def _validate_trading_type(self, proposal):
        if proposal['value'] not in ('live', 'simulation', 'backtest'):
            raise TraitError(f'Invalid trading type: {proposal["value"]}')
        return proposal['value']

    @validate('exchanges')
    def _validate_exchanges(self, proposal):
        for exch in proposal['value']:
            if not isinstance(exch, Exchange):
                raise TraitError(f'Invalid exchange type: {exch}')
        return proposal['value']

    def __init__(self, **config):
        self.verbose = bool(config.get('general', {}).get('verbose', False))
        self.trading_type = config.get('general', {}).get('trading_type', 'simulation')
        self.exchanges = [Exchange.exchanges(_.lower())(self) for _ in config.get('exchange', {}).get('exchanges', [])]

        self.event_loop = asyncio.get_event_loop()

    async def run(self):
        await asyncio.gather(*(asyncio.create_task(exch.connect()) for exch in self.exchanges))

        async with merge(*(exch.tick() for exch in self.exchanges)).stream() as stream:
            async for message in stream:
                print(message)

    def start(self):
        try:
            if self.event_loop.is_running():
                # return future
                return asyncio.create_task(self.run())
            # block until done
            return self.event_loop.run_until_complete(self.run())
        except KeyboardInterrupt:
            return