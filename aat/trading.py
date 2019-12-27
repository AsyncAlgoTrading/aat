import asyncio
import tornado
import uvloop
from .backtest import Backtest
from .callback import Print
from .config import TradingEngineConfig
from .enums import TradingType, Side, CurrencyType, TradeResult
from .execution import Execution
from .query import QueryEngine
from .risk import Risk
from .strategy import TradingStrategy
from .structs import TradeRequest, TradeResponse
from .ui.server import ServerApplication
from .utils import ex_type_to_ex, iterate_accounts
from .logging import log


class TradingEngine(object):
    def __init__(self, options: TradingEngineConfig, ui_handlers: list = None, ui_settings: dict = None) -> None:
        # save UI class for later
        ui_handlers = ui_handlers or []
        ui_settings = ui_settings or {}
        self._ui_handlers = ui_handlers
        self._ui_settings = ui_settings

        # trading type
        self.trading_type = options.type

        # instantiate exchange instance
        self.exchanges = {o: ex_type_to_ex(o)(o, options.exchange_options) for o in options.exchange_options.exchange_types}

        # lookup by exchange or currency
        self.accounts = {}
        for ex in self.exchanges.values():
            self.accounts[ex._exchange] = {}
            for account in ex.accounts().values():
                self.accounts[ex._exchange][account.currency] = account
                if account.currency not in self.accounts:
                    self.accounts[account.currency] = {}
                self.accounts[account.currency][ex._exchange] = account

        # get account information and balances
        for account in iterate_accounts(self.accounts):
            if self.trading_type == TradingType.BACKTEST:
                log.info(f'Adjusting account balance to 1,000 {account}')
                account.balance = 1000

            if account.currency == CurrencyType.USD:
                log.info(f'Adjusting account balance to 100,000 {account}')
                # if holding USD, add value
                account.balance = 100000
                account.value = account.balance
                options.risk_options.total_funds += account.balance
            else:
                log.info(f'Adjusting account balance to 1,000 {account}')
                account.balance = 1000

                # calculate USD value
                ex = self.exchanges[account.exchange]
                spot = ex.ticker(currency=account.currency)['last']
                options.risk_options.total_funds += account.balance * spot
                account.value = account.balance * spot

        log.info(self.accounts)
        log.info("Running with %.2f USD" % options.risk_options.total_funds)

        # instantiate backtest engine
        self.backtest = Backtest(options.backtest_options) if self.trading_type == TradingType.BACKTEST else None

        # instantiate riskengine
        self.risk = Risk(options.risk_options, self.exchanges, self.accounts)

        # instantiate execution engine
        self.execution = Execution(options.execution_options, self.exchanges, self.accounts)

        # instantiate query engine
        self.query = QueryEngine(trading_type=self.trading_type,
                                 exchanges=self.exchanges,
                                 pairs=options.exchange_options.currency_pairs,
                                 accounts=self.accounts,
                                 instruments={name:
                                              list(set(options.exchange_options.instruments).intersection(
                                                  ex.markets())) for name, ex in self.exchanges.items()},
                                 risk=self.risk,
                                 execution=self.execution)

        # register query hooks
        if self.trading_type in (TradingType.LIVE, TradingType.SIMULATION, TradingType.SANDBOX):
            for exc in self.exchanges.values():

                # Track my trades and cancels for future callbacks
                exc.onTrade(self.query.onTrade)
                exc.onCancel(self.query.onCancel)

                if options.print:
                    exc.registerCallback(Print(onTrade=True, onReceived=True, onOpen=True, onFill=True, onCancel=True, onChange=True, onError=False))
        else:
            self.backtest.onTrade(self.query.onTrade)
            self.backtest.onCancel(self.query.onCancel)
            self.backtest.registerCallback(Print())

        # register strategies from config
        for x in options.strategy_options:
            log.critical('Registering strategy: %s', str(x.clazz))
            x.kwargs['query'] = self.query
            x.kwargs['exchanges'] = self.exchanges
            self.registerStrategy(x.clazz(*x.args, **x.kwargs))

        # actively trading or halted?
        self._trading = True  # type: bool

    def haltTrading(self):
        self._trading = False
        for strat in self.query.strategies:
            strat.onHalt()

    def continueTrading(self):
        self._trading = True
        for strat in self.query.strategies:
            strat.onContinue()

    def registerStrategy(self, strat: TradingStrategy):
        if self.trading_type in (TradingType.LIVE, TradingType.SIMULATION, TradingType.SANDBOX):
            # register for exchange data
            for ex in self.exchanges.values():
                ex.registerCallback(strat.callback())
        else:
            # register for backtest data
            self.backtest.registerCallback(strat.callback())

        # add to tickables
        self.query.registerStrategy(strat)

        # give self to strat so it can request trading actions
        strat.setEngine(self)

    def run(self):
        if self.trading_type in (TradingType.LIVE, TradingType.SIMULATION, TradingType.SANDBOX):
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

            loop = tornado.platform.asyncio.AsyncIOMainLoop().install()

            port = 8081
            self.application = ServerApplication(self,
                                                 extra_handlers=self._ui_handlers,
                                                 custom_settings=self._ui_settings)

            # trigger starts
            for strat in self.query.strategies:
                strat.onStart()

            # run on exchange
            async def _run():
                await asyncio.wait([ex.run(self) for ex in self.exchanges.values()])

            # get event loop
            loop = asyncio.get_event_loop()

            # hook in tornado to asyncio
            log.critical('')
            log.critical('Server listening on port: %s', port)
            log.critical('')
            self.application.listen(port)

            # run asyncio loop
            loop.create_task(_run())
            loop.run_forever()

        else:
            # trigger starts
            for strat in self.query.strategies:
                strat.onStart()

            # let backtester run
            self.backtest.run(self)

    def terminate(self):
        for strat in self._strats:
            strat.onExit()

    def _request(self,
                 side: Side,
                 req: TradeRequest,
                 strat=None):
        self.query.push_tradereq(req)

        if not self._trading:
            # not allowed to trade right now
            log.info('Trading not allowed')
            resp = TradeResponse(request=req,
                                 side=req.side,
                                 exchange=req.exchange,
                                 volume=0.0,
                                 price=0.0,
                                 instrument=req.instrument,
                                 strategy=strat,
                                 order_id='')
        else:
            # get risk report
            resp = self.risk.request(req)

            if resp.risk_check:
                log.info(f'Risk check passed: {resp}')
                # if risk passes, let execution execute
                # Note that the Risk+Execution must be atomic
                # so that the risk module can keep an up-to-date
                # calculation of outstanding risk
                resp = self.execution.request(resp)

                if resp.status == TradeResult.PENDING:
                    # listen for later fill/cancel
                    log.info(f'Order pending: {resp}')
                    self.query.newPending(resp)

                elif resp.status == TradeResult.REJECTED:
                    # send response
                    log.info(f'Trade rejected: {resp}')
                    resp = TradeResponse(request=resp,
                                         side=resp.side,
                                         exchange=req.exchange,
                                         volume=0.0,
                                         price=req.price,
                                         time=req.time,
                                         instrument=req.instrument,
                                         status=TradeResult.REJECTED,
                                         strategy=strat,
                                         order_id='')

                    # take the risk off the books
                    self.risk.cancel(resp)

                elif resp.status == TradeResult.FILLED:
                    if self.trading_type in (TradingType.SIMULATION, TradingType.BACKTEST):
                        # adjust response with slippage and transaction cost modeling
                        resp = strat.slippage(resp)

                        # adjust response with slippage and transaction cost modeling
                        resp = strat.transactionCost(resp)

                        # mark as pending
                        self.query.newPending(resp)

                        # force run through query engine
                        self.query.onFill(resp)

                    log.info(f'Trade filled: {resp}')
                    log.info("Slippage - %s" % resp.slippage)
                    log.info("TXN cost - %s" % resp.transaction_cost)

                    # let risk update according to execution details
                    self.risk.update(resp)

            else:
                log.info('Risk check failed')
                resp = TradeResponse(request=resp,
                                     exchange=req.exchange,
                                     side=resp.side,
                                     volume=0.0,
                                     price=0.0,
                                     time=req.time,
                                     instrument=req.instrument,
                                     status=TradeResult.REJECTED,
                                     strategy=strat,
                                     order_id='')

        self.query.push_traderesp(resp)
        self.query.update_positions(resp)
        return resp

    def request(self, req: TradeRequest, strat=None):
        req.strategy = strat
        return self._request(side=req.side,
                             req=req,
                             strat=strat)

    def cancel(self, resp: TradeResponse, strat=None):
        resp = self.execution.cancel(resp)
        return resp

    def cancelAll(self, strat=None):
        resp = self.execution.cancelAll(self._pending)
        return resp
