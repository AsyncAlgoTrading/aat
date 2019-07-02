import asyncio
import threading
import tornado
import operator
from functools import reduce
from .backtest import Backtest
from .callback import Print
from .config import TradingEngineConfig
from .enums import TradingType, Side, CurrencyType, TradeResult
from .exceptions import ConfigException
from .execution import Execution
from .query import QueryEngine
from .risk import Risk
from .strategy import TradingStrategy
from .structs import TradeRequest, TradeResponse
from .ui.server import ServerApplication
from .utils import ex_type_to_ex
from .logging import log


class TradingEngine(object):
    def __init__(self, options: TradingEngineConfig, ui_handlers: list = None, ui_settings: dict = None) -> None:
        # save UI class for later
        ui_handlers = ui_handlers or []
        ui_settings = ui_settings or {}
        self._ui_handlers = ui_handlers
        self._ui_settings = ui_settings

        # running live?
        self._live = options.type == TradingType.LIVE

        # running simulation?
        self._simulation = options.type == TradingType.SIMULATION

        # running sandbox?
        self._sandbox = options.type == TradingType.SANDBOX

        # running backtest?
        self._backtest = options.type == TradingType.BACKTEST

        # instantiate backtest engine
        self._bt = Backtest(options.backtest_options) if self._backtest else None

        # instantiate riskengine
        self._rk = Risk(options.risk_options)

        # instantiate exchange instance
        self._exchanges = {o: ex_type_to_ex(o)(o, options.exchange_options) for o in options.exchange_options.exchange_types}

        # instantiate execution engine
        self._ec = Execution(options.execution_options, self._exchanges)

        # if live or sandbox, get account information and balances
        if self._live or self._simulation or self._sandbox:
            accounts = reduce(operator.concat, [ex.accounts() for ex in self._exchanges.values()])
            for ex in self._exchanges.values():
                for account in ex.accounts():
                    if account.currency == CurrencyType.USD:
                        options.risk_options.total_funds += account.balance
                    else:
                        # calculate USD value
                        spot = ex.ticker(currency=account.currency)['last']
                        options.risk_options.total_funds += account.balance*spot
                        account.value = account.balance*spot

            log.info(accounts)
            log.info("Running with %.2f USD" % options.risk_options.total_funds)

        # instantiate query engine
        self._qy = QueryEngine(backtest=self._backtest,
                               exchanges=self._exchanges,
                               pairs=options.exchange_options.currency_pairs,
                               instruments={name:
                                            list(set(options.exchange_options.instruments).intersection(
                                                ex.markets())) for name, ex in self._exchanges.items()},
                               total_funds=options.risk_options.total_funds)

        # register query hooks
        if self._live or self._simulation or self._sandbox:
            for exc in self._exchanges.values():
                exc.onTrade(self._qy.onTrade)

                if options.print:
                    exc.registerCallback(Print(onTrade=True, onReceived=True, onOpen=True, onFill=True, onCancel=True, onChange=True, onError=False))
        elif self._backtest:
            self._bt.onTrade(self._qy.onTrade)
            self._bt.registerCallback(Print())

        # sanity check
        assert not (self._live and self._simulation and self._sandbox and self._backtest)

        # register strategies from config
        for x in options.strategy_options:
            log.critical('Registering strategy: %s', str(x.clazz))
            self.registerStrategy(x.clazz(*x.args, **x.kwargs))

        # actively trading or halted?
        self._trading = True  # type: bool

    def exchanges(self):
        return self._exchanges

    def backtest(self):
        return self._bt

    def risk(self):
        return self._rk

    def execution(self):
        return self._ec

    def query(self):
        return self._qy

    def haltTrading(self):
        self._trading = False
        for strat in self.query().strategies():
            strat.onHalt()

    def continueTrading(self):
        self._trading = True
        for strat in self.query().strategies():
            strat.onContinue()

    def registerStrategy(self, strat: TradingStrategy):
        if self._live or self._simulation or self._sandbox:
            # register for exchange data
            for ex in self._exchanges.values():
                ex.registerCallback(strat.callback())

        elif self._backtest:
            # register for backtest data
            self._bt.registerCallback(strat.callback())

        # add to tickables
        self.query().registerStrategy(strat)

        # give self to strat so it can request trading actions
        strat.setEngine(self)

    def strategies(self):
        return self.query().strategies()

    def portfolio_value(self) -> list:
        return self.query()._portfolio_value

    def run(self):
        if self._live or self._simulation or self._sandbox:
            port = 8081
            self.application = ServerApplication(self,
                                                 extra_handlers=self._ui_handlers,
                                                 custom_settings=self._ui_settings)
            log.critical('')
            log.critical('Server listening on port: %s', port)
            log.critical('')
            self.application.listen(port)
            self._t = threading.Thread(target=tornado.ioloop.IOLoop.current().start)
            self._t.daemon = True  # So it terminates on exit
            self._t.start()

            # trigger starts
            for strat in self.query().strategies():
                strat.onStart()

            # run on exchange
            async def _run():
                await asyncio.wait([ex.run(self) for ex in self._exchanges.values()])
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(_run())

        elif self._backtest:
            # trigger starts
            for strat in self._strats:
                strat.onStart()

            # let backtester run
            self._bt.run(self)

        else:
            raise ConfigException('Invalid configuration')

    def terminate(self):
        for strat in self._strats:
            strat.onExit()

    def _request(self,
                 side: Side,
                 req: TradeRequest,
                 strat=None):
        self.query().push_tradereq(req)

        if not self._trading:
            # not allowed to trade right now
            log.info('Trading not allowed')
            resp = TradeResponse(request=req,
                                 side=req.side,
                                 exchange=req.exchange,
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
                        log.info('Order pending')
                        self.query().newPending(resp)

                    elif resp.status == TradeResult.REJECTED:
                        # send response
                        log.info('Trade rejected')
                        resp = TradeResponse(request=resp,
                                             side=resp.side,
                                             exchange=req.exchange,
                                             volume=0.0,
                                             price=0.0,
                                             instrument=req.instrument,
                                             status=TradeResult.REJECTED,
                                             order_id='')

                    elif resp.status == TradeResult.FILLED:
                        log.info('Trade filled')
                        log.info("Slippage - %s" % resp)
                        log.info("TXN cost - %s" % resp)
                        # let risk update according to execution details
                        self._rk.update(resp)
                else:
                    # backtesting or simulation
                    resp = TradeResponse(request=req,
                                         side=req.side,
                                         exchange=req.exchange,
                                         volume=req.volume,
                                         price=req.price,
                                         instrument=req.instrument,
                                         status=TradeResult.FILLED,
                                         time=req.time,
                                         order_id='')

                    # adjust response with slippage and transaction cost modeling
                    resp = strat.slippage(resp)
                    log.info("Slippage BT- %s" % resp)

                    resp = strat.transactionCost(resp)
                    log.info("TXN cost BT- %s" % resp)
            else:
                log.info('Risk check failed')
                resp = TradeResponse(request=resp,
                                     exchange=req.exchange,
                                     side=resp.side,
                                     volume=0.0,
                                     price=0.0,
                                     instrument=req.instrument,
                                     status=TradeResult.REJECTED,
                                     order_id='')
        self.query().push_traderesp(resp)
        self.query().update_holdings(resp)
        return resp

    def requestBuy(self, req: TradeRequest, strat=None):
        self._request(side=Side.BUY,
                      req=req,
                      strat=strat)

    def requestSell(self, req: TradeRequest, strat=None):
        self._request(side=Side.SELL,
                      req=req,
                      strat=strat)

    def cancel(self, resp: TradeResponse, strat=None):
        resp = self._ec.cancel(resp)
        return resp

    def cancelAll(self, strat=None):
        resp = self._ec.cancelAll(self._pending)
        return resp
