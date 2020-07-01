import asyncio
import os
import os.path
from aiostream.stream import merge  # type: ignore
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from traitlets.config.application import Application  # type: ignore
from traitlets import validate, TraitError, Unicode, Bool, List, Instance  # type: ignore
from tornado.web import StaticFileHandler, RedirectHandler, Application as TornadoApplication

try:
    from perspective import PerspectiveManager, PerspectiveTornadoHandler  # type: ignore
except ImportError:
    PerspectiveManager, PerspectiveTornadoHandler = None, None  # type: ignore

from .manager import Manager
from ..execution import OrderManager
from ..handler import EventHandler, PrintHandler
from ..models import Event, Error
from ..portfolio import PortfolioManager
from ..risk import RiskManager
from ..table import TableHandler
from ...config import EventType, getStrategies, getExchanges
from ...exchange import Exchange
# from aat.strategy import Strategy
from ...ui import ServerApplication

try:
    import uvloop  # type: ignore
except ImportError:
    uvloop = None


class TradingEngine(Application):
    '''A configureable trading application'''
    name = 'AAT'
    description = 'async algorithmic trading engine'

    # Configureable parameters
    verbose = Bool(default_value=True)
    api = Bool(default_value=True)
    port = Unicode(default_value='8080', help="Port to run on").tag(config=True)
    event_loop = Instance(klass=asyncio.events.AbstractEventLoop)
    executor = Instance(klass=ThreadPoolExecutor, args=(4,), kwargs={})

    # Core components
    trading_type = Unicode(default_value='simulation')
    order_manager = Instance(OrderManager, args=(), kwargs={})
    risk_manager = Instance(RiskManager, args=(), kwargs={})
    portfolio_manager = Instance(PortfolioManager, args=(), kwargs={})
    exchanges = List(trait=Instance(klass=Exchange))
    event_handlers = List(trait=Instance(EventHandler), default_value=[])

    # API application
    api_application = Instance(klass=TornadoApplication)
    api_handlers = List(default_value=[])

    table_manager = Instance(klass=PerspectiveManager or object, args=(), kwargs={})  # failover to object

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
        self.port = config.get('general', {}).get('port', self.port)
        self.verbose = bool(int(config.get('general', {}).get('verbose', self.verbose)))
        self.api = bool(int(config.get('general', {}).get('api', self.api)))

        self.trading_type = config.get('general', {}).get('trading_type', 'simulation')
        self.exchanges = getExchanges(config.get('exchange', {}).get('exchanges', []), verbose=self.verbose)
        self.manager = Manager(self, self.trading_type, self.exchanges)

        # set event loop to use uvloop
        if uvloop:
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

        # install event loop
        self.event_loop = asyncio.get_event_loop()

        # setup subscriptions
        self._subscriptions = {m: [] for m in EventType.__members__.values()}

        # install event handlers
        strategies = getStrategies(config.get('strategy', {}).get('strategies', []))
        for strategy in strategies:
            self.log.critical("Installing strategy: {}".format(strategy))
            self.registerHandler(strategy)

        # warn if no event handlers installed
        if not self.event_handlers:
            self.log.critical('Warning! No event handlers set')

        # register internal management event handler
        self.registerHandler(self.manager)

        # install print handler if verbose
        if self.verbose:
            self.log.critical('Installing print handler')
            self.registerHandler(PrintHandler())

        # install webserver
        if self.api:
            self.log.critical('Installing API handlers')

            if PerspectiveManager is not None:
                table_handler = TableHandler()
                table_handler.installTables(self.table_manager)
                self.registerHandler(table_handler)

            self.api_handlers.append((r"/", RedirectHandler, {"url": "/index.html"}))
            self.api_handlers.append((r"/api/v1/ws", PerspectiveTornadoHandler, {"manager": self.table_manager, "check_origin": True}))
            self.api_handlers.append((r"/static/js/(.*)", StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), '..', '..', 'ui', 'assets', 'static', 'js')}))
            self.api_handlers.append((r"/static/css/(.*)", StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), '..', '..', 'ui', 'assets', 'static', 'css')}))
            self.api_handlers.append((r"/static/fonts/(.*)", StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), '..', '..', 'ui', 'assets', 'static', 'fonts')}))
            self.api_handlers.append((r"/(.*)", StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), '..', '..', 'ui', 'assets', 'static', 'html')}))
            self.api_application = ServerApplication(handlers=self.api_handlers)
            self.log.critical('.......')
            self.log.critical(f'listening on 0.0.0.0:{self.port}')
            self.log.critical('.......')
            self.api_application.listen(self.port)

    def registerHandler(self, handler):
        '''register a handler and all callbacks that handler implements

        Args:
            handler (EventHandler): the event handler to register
        Returns:
            value (EventHandler or None): event handler if its new, else None
        '''
        if handler not in self.event_handlers:
            # append to handler list
            self.event_handlers.append(handler)

            # register callbacks for event types
            for type in EventType.__members__.values():
                # get callback, could be none if not implemented
                cb = handler.callback(type)
                if cb:
                    self.registerCallback(type, cb)

            handler._setManager(self.manager)
            return handler
        return None

    def _make_async(self, function):
        async def _wrapper(event):
            return await self.event_loop.run_in_executor(self.executor, function, event)
        return _wrapper

    def registerCallback(self, event_type, callback):
        '''register a callback for a given event type

        Args:
            event_type (EventType): event type enum value to register
            callback (function): function to call on events of `event_type`
        Returns:
            value (bool): True if registered (new), else False
        '''
        if callback not in self._subscriptions[event_type]:
            if not asyncio.iscoroutinefunction(callback):
                callback = self._make_async(callback)
            self._subscriptions[event_type].append(callback)
            return True
        return False

    def pushEvent(self, event):
        '''push non-exchange event into the queue'''
        self._queued_events.append(event)

    async def run(self):
        '''run the engine'''
        # setup future queue
        self._queued_events = deque()

        # await all connections
        await asyncio.gather(*(asyncio.create_task(exch.connect()) for exch in self.exchanges))

        # send start event to all callbacks
        await self.tick(Event(type=EventType.START, target=None))

        async with merge(*(exch.tick() for exch in self.exchanges)).stream() as stream:
            # stream through all events
            async for event in stream:
                # tick exchange event to handlers
                await self.tick(event)

                # process any secondary events
                while self._queued_events:
                    event = self._queued_events.popleft()
                    await self.tick(event)

    async def tick(self, event):
        '''send an event to all registered event handlers

        Arguments:
            event (Event): event to send
        '''
        for handler in self._subscriptions[event.type]:
            try:
                await handler(event)
            except KeyboardInterrupt:
                raise
            except SystemExit:
                raise
            except BaseException as e:
                if event.type == EventType.ERROR:
                    # don't infinite error
                    raise
                await self.tick(Event(type=EventType.ERROR, target=Error(target=event, handler=handler, exception=e)))
                await asyncio.sleep(1)

    def start(self):
        try:
            # if self.event_loop.is_running():
            #     # return future
            #     return asyncio.create_task(self.run())
            # block until done
            self.event_loop.run_until_complete(self.run())
        except KeyboardInterrupt:
            pass
        # send exit event to all callbacks
        asyncio.ensure_future(self.tick(Event(type=EventType.EXIT, target=None)))
