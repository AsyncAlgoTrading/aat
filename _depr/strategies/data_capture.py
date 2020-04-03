from ..strategy import TradingStrategy
from ..structs import MarketData, TradeResponse
from ..logging import log


class DataCaptureStrategy(TradingStrategy):
    def __init__(self, filename, *args, **kwargs) -> None:
        super(DataCaptureStrategy, self).__init__(*args, **kwargs)
        self.filename = filename

    def onTrade(self, data: MarketData) -> bool:
        log.info(data)

    def onError(self, e) -> None:
        log.critical(e, type(e))

    def onExit(self) -> None:
        self.cancelAll(lambda *args: True)

    def onChange(self, data: MarketData) -> None:
        log.info(data)

    def onFill(self, res: TradeResponse) -> None:
        log.info(res)

    def onCancel(self, data: MarketData) -> None:
        log.info(data)

    def onOpen(self, data: MarketData) -> None:
        log.info(data)

    def slippage(self, resp: TradeResponse) -> TradeResponse:
        return resp

    def transactionCost(self, resp: TradeResponse) -> TradeResponse:
        return resp

    def onAnalyze(self, engine) -> None:
        pass
