import pandas as pd
import time
import tqdm
from .config import BacktestConfig
from .data_source import StreamingDataSource
from .logging import log
from .structs import MarketData, Instrument
from .enums import PairType, TickType, ExchangeType_from_string, Side


def line_to_data(record):
    data = MarketData(time=record.name[0],
                      volume=record.volume,
                      price=record.close,
                      type=TickType.TRADE,
                      instrument=Instrument(underlying=PairType.from_string(record.name[1])),
                      exchange=ExchangeType_from_string(record.exchange),
                      side=Side.NONE)
    return data


class Backtest(StreamingDataSource):
    def __init__(self, options: BacktestConfig) -> None:
        super(Backtest, self).__init__()

    def run(self, engine) -> None:
        log.info('Starting....')

        datas = []
        iterable = [(e, c) for e in engine.exchanges.values() for c in e.options().currency_pairs]
        for ex, currency in tqdm.tqdm(iterable, desc="Fetching backtest data"):
            datas.append(ex.historical(currency_pairs=[currency]))
        data = pd.concat(datas)
        data.sort_index(level=0, inplace=True)  # sort according to date, so that multiple symbols prices can be bundled

        for index, row in data.iterrows():
            self.receive(line_to_data(row))
        log.info('Backtest done, running analysis.')

        self.callback(TickType.ANALYZE, engine)
        log.info('Analysis completed.')

    def receive(self, data: MarketData) -> None:
        # TODO allow if market data for bid/ask
        if data.type == TickType.TRADE:
            self.callback(TickType.TRADE, data)
        else:
            self.callback(TickType.ERROR, data)

    def close(self) -> None:
        pass

    def seqnum(self, num: int) -> None:
        pass

    def tickToData(self, tick: str) -> None:
        pass
