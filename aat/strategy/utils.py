from ..config import Side, TradingType
from ..core import Trade, Instrument, ExchangeType, StrategyManager


class StrategyUtilsMixin(object):
    _manager: StrategyManager

    def orders(self, instrument: Instrument = None, exchange: ExchangeType = None, side: Side = None):
        '''select all open orders

        Args:
            instrument (Optional[Instrument]): filter open orders by instrument
            exchange (Optional[ExchangeType]): filter open orders by exchange
            side (Optional[Side]): filter open orders by side
        Returns:
            list (Order): list of open orders
        '''
        return self._manager.orders(self, instrument, exchange, side)

    def pastOrders(self, instrument: Instrument = None, exchange: ExchangeType = None, side: Side = None):
        '''select all past orders

        Args:
            instrument (Optional[Instrument]): filter past orders by instrument
            exchange (Optional[ExchangeType]): filter past orders by exchange
            side (Optional[Side]): filter past orders by side
        Returns:
            list (Order): list of open orders
        '''
        return self._manager.pastOrders(self, instrument, exchange, side)

    def trades(self, instrument: Instrument = None, exchange: ExchangeType = None, side: Side = None):
        '''select all past trades

        Args:
            instrument (Optional[Instrument]): filter trades by instrument
            exchange (Optional[ExchangeType]): filter trades by exchange
            side (Optional[Side]): filter trades by side
        Returns:
            list (Trade): list of trades
        '''
        return self._manager.trades(self, instrument, exchange, side)

    ################
    # Risk Methods #
    ################
    def positions(self, instrument: Instrument = None, exchange: ExchangeType = None, side: Side = None):
        '''select all positions

        Args:
            instrument (Instrument): filter positions by instrument
            exchange (ExchangeType): filter positions by exchange
            side (Side): filter positions by side
        Returns:
            list (Position): list of positions
        '''
        return self._manager.positions(instrument=instrument, exchange=exchange, side=side)

    def risk(self, position=None):
        '''Get risk metrics

        Args:
            position (Position): only get metrics on this position
        Returns:
            dict: metrics
        '''
        return self._manager.risk(position=position)

    def priceHistory(self, instrument: Instrument = None):
        '''Get price history for asset

        Args:
            instrument (Instrument): get price history for instrument
        Returns:
            DataFrame: price history
        '''
        return self._manager.priceHistory(instrument=instrument)

    #################
    # Other Methods #
    #################
    def tradingType(self) -> TradingType:
        '''Return the trading type, from TradingType enum'''
        return self._manager.tradingType()

    def now(self):
        '''Return the current datetime. Useful to avoid code changes between
        live trading and backtesting. Defaults to `datetime.now`'''
        return self._manager.now()

    def instruments(self, type=None, exchange=None):
        '''Return list of all available instruments'''
        return Instrument._instrumentdb.instruments(type=type, exchange=exchange)

    def exchanges(self, instrument_type=None):
        '''Return list of all available exchanges'''
        return list(set(__ for _ in Instrument._instrumentdb.instruments(type=instrument_type) for __ in _.exchanges))

    def accounts(self, type=None, exchange=None):
        '''Return list of all accounts'''
        raise NotImplementedError()

    def subscribe(self, instrument=None):
        '''Subscribe to market data for the given instrument'''
        return self._manager.subscribe(instrument=instrument, strategy=self)

    async def lookup(self, instrument, exchange=None):
        '''Return list of all available instruments that match the instrument given'''
        return await self._manager.lookup(instrument, exchange=exchange)

    def slippage(self, trade: Trade):
        '''method to inject slippage when backtesting

        Args:
            trade (Trade): the completed trade to adjust
        Returns:
            trade (Trade): the modified trade
        '''
        pass

    def transactionCost(self, trade: Trade):
        '''method to inject transaction costs when backtesting

        Args:
            trade (Trade): the completed trade to adjust
        Returns:
            trade (Trade): the modified trade
        '''
        pass
