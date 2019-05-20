import asyncio
import threading
import tornado
import operator
from functools import reduce
from typing import Callable
from .backtest import Backtest
from .callback import Print
from .config import TradingEngineConfig
from .enums import TradingType, Side, CurrencyType, TradeResult, OrderType
from .execution import Execution
from .risk import Risk
from .strategy import TradingStrategy
from .structs import TradeRequest, TradeResponse
from .utils import ex_type_to_ex
from .logging import LOG as log, SLIP as sllog, TXNS as tlog
from .ui.server import ServerApplication


class TradingEngine(object):
    def __init__(self, options: TradingEngineConfig) -> None:
        # running live?
        self._live = options.type == TradingType.LIVE

        # running simulation?
        self._simulation = options.type == TradingType.SIMULATION

        # running sandbox?
        self._sandbox = options.type == TradingType.SANDBOX

        # running backtest?
        self._backtest = options.type == TradingType.BACKTEST

        # the strategies to run
        self._strats = []

        # instantiate backtest engine
        self._bt = Backtest(options.backtest_options) if self._backtest else None

        # instantiate riskengine
        self._rk = Risk(options.risk_options)

        # instantiate exchange instance
        self._exchanges = {o: ex_type_to_ex(o)(o, options.exchange_options) for o in options.exchange_options.exchange_types}

        # if live or sandbox, get account information and balances
        if self._live or self._simulation or self._sandbox:
            accounts = reduce(operator.concat, [ex.accounts() for ex in self._exchanges.values()])
            # extract max funds info
            for account in accounts:
                if account.currency == CurrencyType.USD:
                    # TODO multiple USD accounts?
                    options.risk_options.total_funds += account.balance

            log.info(accounts)
            log.info("Running with %.2f USD" % options.risk_options.total_funds)

        # instantiate execution engine
        self._ec = Execution(options.execution_options, self._exchanges)

        # sanity check
        assert not (self._live and self._simulation and self._sandbox and self._backtest)

        # running print callback for debug?
        if options.print:
            log.warn('WARNING: Running in print mode')

            # register a printer callback that prints every message
            if self._live or self._simulation or self._sandbox:
                for ex in self._exchanges:
                    ex.registerCallback(
                        Print(onTrade=True, onReceived=True, onOpen=True, onDone=True, onChange=True, onError=False))
            if self._backtest:
                self._bt.registerCallback(Print())

        # register strategies from config
        for x in options.strategy_options:
            log.critical('Registering strategy: %s', str(x.clazz))
            self.registerStrategy(x.clazz(*x.args, **x.kwargs))

        # actively trading or halted?
        self._trading = True  # type: bool

        # pending orders to process (partial fills)
        self._pending = {OrderType.MARKET: [], OrderType.LIMIT: []}  # TODO in progress

    def exchanges(self):
        return self._exchanges

    def backtest(self):
        return self._bt

    def risk(self):
        return self._rk

    def execution(self):
        return self._ec

    def haltTrading(self):
        self._trading = False

    def continueTrading(self):
        self._trading = True

    def registerStrategy(self, strat: TradingStrategy):
        if self._live or self._simulation or self._sandbox:
            # register for exchange data
            for ex in self._exchanges.values():
                ex.registerCallback(strat.callback())

        elif self._backtest:
            # register for backtest data
            self._bt.registerCallback(strat.callback())

        # add to tickables
        self._strats.append(strat)  # add to tickables

        # give self to strat so it can request trading actions
        strat.setEngine(self)

    def run(self):
        if self._live or self._simulation or self._sandbox:
            port = 8081
            self.application = ServerApplication(self)
            log.critical('')
            log.critical('Server listening on port: %s', port)
            log.critical('')
            self.application.listen(port)
            self._t = threading.Thread(target=tornado.ioloop.IOLoop.current().start)
            self._t.daemon = True  # So it terminates on exit
            self._t.start()

            # run on exchange
            async def _run():
                await asyncio.wait([ex.run(self) for ex in self._exchanges.values()])
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(_run())

        elif self._backtest:
            # let backtester run
            self._bt.run(self)

        else:
            raise Exception('Invalid configuration')

    def terminate(self):
        for strat in self._strats:
            strat.onExit()

    def _request(self,
                 side: Side,
                 callback: Callable,
                 req: TradeRequest,
                 callback_failure=None,
                 strat=None):
        if not self._trading:
            # not allowed to trade right now
            log.info('Trading not allowed')
            resp = TradeResponse(request=req,
                                 side=req.side,
                                 volume=0.0,
                                 price=0.0,
                                 instrument=req.instrument,
                                 success=False,
                                 order_id='')

        else:
            # get risk report
            resp = self._rk.request(req)

            if resp.risk_check:
                log.info('Risk check passed')
                # if risk passes, let execution execute
                if self._live or self._sandbox:
                    # Trading
                    resp = self._ec.request(resp)

                    # TODO
                    if resp.status == TradeResult.PENDING:
                        # listen for later
                        # TODO
                        log.info('Order pending')
                        self._pending[req.order_type].append(resp)  # TODO or req?

                    elif resp.status == TradeResult.REJECTED:
                        # send response
                        log.info('Trade rejected')
                        resp = TradeResponse(request=resp,
                                             side=resp.side,
                                             volume=0.0,
                                             price=0.0,
                                             instrument=req.instrument,
                                             status=TradeResult.REJECTED,
                                             order_id='')

                    elif resp.status == TradeResult.FILLED:
                        log.info('Trade filled')
                        sllog.info("Slippage - %s" % resp)
                        tlog.info("TXN cost - %s" % resp)
                        # let risk update according to execution details
                        self._rk.update(resp)
                else:
                    # backtesting or simulation
                    resp = TradeResponse(request=req,
                                         side=req.side,
                                         volume=req.volume,
                                         price=req.price,
                                         instrument=req.instrument,
                                         status=TradeResult.FILLED,
                                         time=req.time,
                                         order_id='')

                    # register the initial request
                    strat.registerDesire(resp.time, resp.side, resp.price)

                    # adjust response with slippage and transaction cost modeling
                    resp = strat.slippage(resp)
                    sllog.info("Slippage BT- %s" % resp)

                    resp = strat.transactionCost(resp)
                    tlog.info("TXN cost BT- %s" % resp)

                    # register the response
                    strat.registerAction(resp.time, resp.side, resp.price)
            else:
                log.info('Risk check failed')
                resp = TradeResponse(request=resp,
                                     side=resp.side,
                                     volume=0.0,
                                     price=0.0,
                                     instrument=req.instrument,
                                     status=TradeResult.REJECTED,
                                     order_id='')

        callback_failure(resp) if callback_failure and not resp.success else callback(resp)

    def requestBuy(self, callback: Callable, req: TradeRequest, callback_failure=None, strat=None):
        self._request(Side.BUY, callback, req, callback_failure, strat)

    def requestSell(self, callback: Callable, req: TradeRequest, callback_failure=None, strat=None):
        self._request(Side.SELL, callback, req, callback_failure, strat)

    def cancel(self, callback: Callable, resp: TradeResponse, callback_failure=None, strat=None):
        resp = self._ec.cancel(resp)
        callback_failure(resp) if callback_failure and not resp.success else callback(resp)

    def cancelAll(self, callback: Callable, callback_failure=None, strat=None):
        # FIXME iterate through open in order
        resp = self._ec.cancelAll()
        callback_failure(resp) if callback_failure and not resp.success else callback(resp)
