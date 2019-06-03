import ccxt
import logging
import os
import pytz
from datetime import datetime
from enum import Enum
from functools import lru_cache
from .enums import ExchangeType, CurrencyType, OrderType, Side, PairType
from .exceptions import AATException
from .logging import LOG as log, \
                     STRAT as slog, \
                     DATA as dlog, \
                     RISK as rlog, \
                     EXEC as exlog, \
                     SLIP as sllog, \
                     TXNS as tlog, \
                     MANUAL as mlog, \
                     ERROR as elog

@lru_cache(None)
def parse_date(indate: str) -> datetime:
    try:
        date = datetime.utcfromtimestamp(float(indate))
        date = pytz.utc.localize(date).astimezone(
            pytz.timezone('EST')).replace(tzinfo=None)
    except ValueError:
        date = datetime.strptime(indate, "%Y-%m-%dT%H:%M:%S.%fZ")
    return date


@lru_cache(None)
def ex_type_to_ex(ex: ExchangeType):
    if ex == ExchangeType.COINBASE:
        from .exchanges.coinbase import CoinbaseExchange
        return CoinbaseExchange
    elif ex == ExchangeType.GEMINI:
        from .exchanges.gemini import GeminiExchange
        return GeminiExchange
    elif ex == ExchangeType.KRAKEN:
        from .exchanges.kraken import KrakenExchange
        return KrakenExchange
    raise NotImplementedError(f'Exchange type not implemented : {ex} ')


@lru_cache(None)
def get_keys_from_environment(prefix: str) -> tuple:
    key = os.environ[prefix + '_API_KEY']
    secret = os.environ[prefix + '_API_SECRET']
    passphrase = os.environ[prefix + '_API_PASS']
    return key, secret, passphrase


@lru_cache(None)
def str_to_currency_type(s: str) -> CurrencyType:
    s = s.upper()
    if s not in CurrencyType.members():
        raise AATException(f'CurrencyType not recognized {s}')
    return CurrencyType(s)


@lru_cache(None)
def str_to_currency_pair_type(s: str) -> PairType:
    return PairType.from_string(s)


@lru_cache(None)
def str_currency_to_currency_pair_type(s: str, base: str = 'USD') -> PairType:
    return PairType.from_string(s, base)


@lru_cache(None)
def str_to_side(s: str) -> Side:
    s = s.upper()
    if 'BUY' in s or 'BID' in s:
        return Side.BUY
    if 'SELL' in s or 'ASK' in s:
        return Side.SELL
    return Side.NONE


@lru_cache(None)
def str_to_order_type(s: str) -> OrderType:
    s = s.upper()
    if 'MARKET' in s:
        return OrderType.MARKET
    if 'LIMIT' in s:
        return OrderType.LIMIT
    return OrderType.NONE


@lru_cache(None)
def str_to_exchange(exchange: str) -> ExchangeType:
    if exchange.upper() not in ExchangeType.members():
        raise AATException(f'Exchange not recognized: {exchange}')
    return ExchangeType(exchange.upper())


def set_verbose(level):
    # Print/log extra info
    # olog.propagate = True
    # slog.propagate = True
    # elog.propagate = True
    # dlog.propagate = False  # too much
    # tlog.propagate = True
    # mlog.propagate = True
    if level >= 2:
        log.setLevel(logging.DEBUG)
        slog.setLevel(logging.DEBUG)
        dlog.setLevel(logging.DEBUG)
        rlog.setLevel(logging.DEBUG)
        exlog.setLevel(logging.DEBUG)
        sllog.setLevel(logging.DEBUG)
        tlog.setLevel(logging.DEBUG)
        mlog.setLevel(logging.DEBUG)
        elog.setLevel(logging.DEBUG)
    elif level == 1:
        log.setLevel(logging.INFO)
        slog.setLevel(logging.INFO)
        dlog.setLevel(logging.INFO)
        rlog.setLevel(logging.INFO)
        exlog.setLevel(logging.INFO)
        sllog.setLevel(logging.INFO)
        tlog.setLevel(logging.INFO)
        mlog.setLevel(logging.INFO)
        elog.setLevel(logging.INFO)
    log.info('running in verbose mode!')


def trade_req_to_params(req) -> dict:
    ret = {}
    ret['symbol'] = str(req.instrument.underlying)
    ret['side'] = 'buy' if req.side == Side.BUY else 'sell'
    ret['type'] = 'market' if req.order_type == OrderType.MARKET else 'limit'
    ret['amount'] = req.volume

    if ret['type'] == 'limit':
        ret['price'] = req.price

    return ret


def exchange_type_to_ccxt_client(exchange_type):
    if exchange_type == ExchangeType.COINBASE:
        return ccxt.coinbasepro
    elif exchange_type == ExchangeType.GEMINI:
        return ccxt.gemini
    elif exchange_type == ExchangeType.KRAKEN:
        return ccxt.kraken
    elif exchange_type == ExchangeType.POLONIEX:
        return ccxt.poloniex


def tradereq_to_ccxt_order(req) -> dict:
    # TODO order_sub_type
    return dict(
        symbol=str(req.instrument.underlying),
        type=req.order_type.value.lower(),
        side=req.side.value.lower(),
        price=req.price,
        amount=req.volume,
        params={})


def findpath(inst, markets):
    '''find a path from left side of instrument to right side of instrument
    given the available markets

    Args:
        inst: Instrument with an underlying pairtype
        markets: List of Instruments
    Returns:
        tuple:
            instrument1, instrument2, invert pair1, invert pair2
    '''
    from .structs import Instrument
    # should do dijkstras to get cheapest path but im lazy
    currency_from = inst.underlying.value[0]
    currency_to = inst.underlying.value[1]
    c1_btc = Instrument(underlying=PairType((currency_from, CurrencyType.BTC)))
    c1_btc_inv = Instrument(underlying=PairType((CurrencyType.BTC, currency_from)))
    c2_btc = Instrument(underlying=PairType((CurrencyType.BTC, currency_to)))
    c2_btc_inv = Instrument(underlying=PairType((currency_to, CurrencyType.BTC)))
    if currency_from == CurrencyType.BTC or \
       currency_to == CurrencyType.BTC or \
       (c1_btc not in markets and c1_btc_inv not in markets) or \
       (c2_btc not in markets and c2_btc_inv not in markets):
        raise AATException(f'Need BTC for intermediary: {inst}')

    return {(True, True):   (c1_btc_inv, c2_btc_inv, True, True),
            (True, False):  (c1_btc_inv, c2_btc, True, False),
            (False, True):  (c1_btc, c2_btc_inv, False, True),
            (False, False): (c1_btc, c2_btc, False, False)}.get((c1_btc not in markets,
                                                                 c2_btc not in markets))
