from ..strategy import TradingStrategy
from ..structs import MarketData, TradeResponse
from ..logging import STRAT as slog, ERROR as elog


class DataCaptureStrategy(TradingStrategy):
    def __init__(self, filename) -> None:
        super(DataCaptureStrategy, self).__init__()
        self.filename = filename

    def onBuy(self, res: TradeResponse) -> None:
        slog.info(res)

    def onSell(self, res: TradeResponse) -> None:
        slog.info(res)

    def onTrade(self, data: MarketData) -> bool:
        slog.info(data)

    def onError(self, e) -> None:
        elog.critical(e, type(e))

    def onExit(self) -> None:
        self.cancelAll(lambda *args: True)

    def onChange(self, data: MarketData) -> None:
        slog.info(data)

    def onFill(self, data: MarketData) -> None:
        slog.info(data)

    def onCancel(self, data: MarketData) -> None:
        slog.info(data)

    def onOpen(self, data: MarketData) -> None:
        slog.info(data)

    def slippage(self, resp: TradeResponse) -> TradeResponse:
        return resp

    def transactionCost(self, resp: TradeResponse) -> TradeResponse:
        return resp

    def onAnalyze(self, _) -> None:
        pass
