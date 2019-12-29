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
}.get((name, typ), None))
