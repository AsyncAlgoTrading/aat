import sys
from .config import parseConfig
from .core import TradingEngine


def main(argv: list) -> None:
    # Parse the command line config
    config = parseConfig(argv)

    # Instantiate trading engine
    #
    # The engine is responsible for managing the different components,
    # including the strategies, the bank/risk engine, and the
    # exchange/backtest engine.
    engine = TradingEngine(**config)

    # Run the live trading engine
    engine.start()


if __name__ == '__main__':
    main(sys.argv)
