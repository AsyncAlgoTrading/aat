from functools import lru_cache
from .enums import ExchangeType, TradingType


EXCHANGE_MARKET_DATA_ENDPOINT = lru_cache(None)(lambda name, typ: {  # noqa: E731
    (ExchangeType.COINBASE, TradingType.SANDBOX): 'wss://ws-feed-public.sandbox.pro.coinbase.com',
    (ExchangeType.COINBASE, TradingType.LIVE): 'wss://ws-feed.pro.coinbase.com',
    (ExchangeType.COINBASE, TradingType.SIMULATION): 'wss://ws-feed.pro.coinbase.com',

    (ExchangeType.GEMINI, TradingType.SANDBOX): 'wss://api.sandbox.gemini.com/v1/marketdata/%s?heartbeat=true',
    (ExchangeType.GEMINI, TradingType.LIVE): 'wss://api.gemini.com/v1/marketdata/%s?heartbeat=true',
    (ExchangeType.GEMINI, TradingType.SIMULATION): 'wss://api.gemini.com/v1/marketdata/%s?heartbeat=true',

    (ExchangeType.KRAKEN, TradingType.SANDBOX): 'wss://ws-beta.kraken.com',
    (ExchangeType.KRAKEN, TradingType.LIVE): 'wss://ws.kraken.com',
    (ExchangeType.KRAKEN, TradingType.SIMULATION): 'wss://ws.kraken.com',

    (ExchangeType.POLONIEX, TradingType.SANDBOX): '',
    (ExchangeType.POLONIEX, TradingType.LIVE): 'wss://api2.poloniex.com',
    (ExchangeType.POLONIEX, TradingType.SIMULATION): 'wss://api2.poloniex.com',

    # (ExchangeType.DERIBIT, TradingType.SANDBOX): 'wss://test.deribit.com/ws/api/v1/',
    # (ExchangeType.DERIBIT, TradingType.LIVE): 'wss://www.deribit.com/ws/api/v1/',
    # (ExchangeType.DERIBIT, TradingType.SIMULATION): 'wss://www.deribit.com/ws/api/v1/',

}.get((name, typ), None))
