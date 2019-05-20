import pandas as pd
from .config import BacktestConfig
from .data_source import StreamingDataSource
from .logging import LOG as log, DATA as dlog
from .structs import MarketData, Instrument
from .enums import PairType, TickType, ExchangeType, Side


def line_to_data(record):
    data = MarketData(time=record.name[0],
                      price=record.volume,
                      volume=record.close,
                      type=TickType.TRADE,
                      instrument=Instrument(underlying=PairType.from_string(record.name[1])),
                      exchange=ExchangeType(record.exchange),
                      side=Side.NONE)
    return data


class Backtest(StreamingDataSource):
    def __init__(self, options: BacktestConfig) -> None:
        super(Backtest, self).__init__()

    def run(self, engine) -> None:
        log.info('Starting....')

        datas = [ex.historical() for ex in engine.exchanges().values()]
        data = pd.concat(datas)
        data.sort_index()

        for index, row in data.iterrows():
            self.receive(line_to_data(row))
        log.info('Backtest done, running analysis.')
        self.callback(TickType.ANALYZE, None)
        log.info('Analysis completed.')

    def receive(self, data: MarketData) -> None:
        # TODO allow if market data for bid/ask
        if data.type == TickType.TRADE:
            self.callback(TickType.TRADE, data)
            dlog.info(data)

        else:
            self.callback(TickType.ERROR, data)

    def close(self) -> None:
        pass

    def seqnum(self, num: int) -> None:
        pass

    def tickToData(self, tick: str) -> None:
        pass
