import logging
import os
import pytz
from datetime import datetime
from enum import Enum
from functools import lru_cache
from .enums import ExchangeType, CurrencyType, OrderType, Side, PairType
from .logging import LOG as log, \
                     STRAT as slog, \
                     DATA as dlog, \
                     RISK as rlog, \
                     EXEC as exlog, \
                     SLIP as sllog, \
                     TXNS as tlog, \
                     MANUAL as mlog, \
                     ERROR as elog

NOPRINT = True


def create_pair(key: str, typ: type, default=None, container=None) -> property:
    def get(self):
        if hasattr(self, '__' + str(key)):
            return getattr(self, '__' + str(key))
        if default is not None and (type(default) == typ or (container == list and (default == [] or type(default[0]) == typ))):
            if container:
                if container == list:
                    return default
                else:
                    raise TypeError('Unrecognized container: %s',
                                    str(container))
            return default
        raise TypeError("%s is unset" % key)

    def set(self, val):
        if container:
            if container == list:
                if not isinstance(val, list) or not all(map(
                        lambda x: isinstance(x, typ), val)):
                    raise TypeError("%s attribute must be set to an "
                                    "instance of %s" % (key, typ))
            else:
                raise TypeError('Unrecognized container: %s',
                                str(container))
        else:
            if not isinstance(val, typ) and not type(val) == typ:
                raise TypeError("%s attribute must be set to an instance of %s"
                                % (key, typ))
        setattr(self, '__' + str(key), val)
    return property(get, set)


def config(cls):
    new_cls_dict = {}
    vars = []
    for k, v in cls.__dict__.items():
        if isinstance(v, type):
            # V is a type, no default value
            v = create_pair(k, v)
            vars.append(k)
        elif isinstance(v, tuple) and \
                isinstance(v[0], type) and \
                isinstance(v[1], v[0]):
            # v is a pair, (type, instance)
            v = create_pair(k, v[0], v[1])
            vars.append(k)
        elif isinstance(v, list) and \
                isinstance(v[0], type):
            # v is a list [type]
            v = create_pair(k, v[0], container=list)
            vars.append(k)
        elif isinstance(v, tuple) and \
                isinstance(v[0], list) and \
                isinstance(v[0][0], type) and \
                isinstance(v[1], list):
            # v is a pair,  ([type], [instance?])
            if len(v[1]) > 0 and isinstance(v[1][0], v[0][0]):  # TODO check all
                v = create_pair(k, v[0][0], v[1], container=list)
                vars.append(k)
            elif v[1] == []:
                v = create_pair(k, v[0][0], v[1], container=list)
                vars.append(k)
            else:
                raise Exception('Unexpected list instance: %s' % v[1][0])

        new_cls_dict[k] = v
    new_cls_dict['__init__'] = __init__config
    new_cls_dict['__repr__'] = __repr__
    new_cls_dict['_vars'] = vars
    new_cls_dict['_excludes'] = []
    return type(cls)(cls.__name__, cls.__bases__, new_cls_dict)


def __init__config(self, **kwargs) -> None:
    for k, v in kwargs.items():
        if k not in self._vars:
            raise Exception('Attribute not found! %s' % k)
    for item in self._vars:
        if item not in kwargs:
            log.debug('WARNING %s unset!', item)
        else:
            setattr(self, item, kwargs.get(item))


def __init__struct(self, **kwargs) -> None:
    for item in self._vars:
        if item not in kwargs:
            pass
            # log.debug('WARNING %s unset!', item)
        else:
            setattr(self, item, kwargs.get(item))

        getattr(self, item)  # make sure all are set.

    for k, v in kwargs.items():
        if k not in self._vars:
            raise Exception('Attribute not found! %s' % k)


def to_dict(self, serializable=False, str_timestamp=False, **kwargs) -> dict:
    from .structs import Instrument, TradeRequest, TradeResponse
    ret = {}
    if serializable:
        for item in self._vars:
            ret[item] = getattr(self, item)
            if isinstance(ret[item], datetime):
                if str_timestamp:
                    ret[item] = ret[item].strftime('%y-%m-%d %H:%M:%S')
                else:
                    ret[item] = round(ret[item].timestamp())
            elif isinstance(ret[item], Instrument) or \
                 isinstance(ret[item], TradeRequest) or \
                 isinstance(ret[item], TradeResponse):
                ret[item] = ret[item].to_dict(serializable, str_timestamp, **kwargs)
            elif isinstance(ret[item], Enum):
                ret[item] = str(ret[item])
            elif isinstance(ret[item], float):
                if ((ret[item] >= float('inf')) is False) and \
                   ((ret[item] <= float('inf')) is False):
                    ret[item] = None
    else:
        for item in self._vars:
            ret[item] = getattr(self, item)
    return ret


def __repr__(self) -> str:
    # log.warn(str(self.__class__))
    return '<' + ', '.join([x + '-' + str(getattr(self, x))
                           for x in self._vars if hasattr(self, x) and
                           x not in self._excludes]) + '>'


def struct(cls):
    new_cls_dict = {}

    vars = []
    excludes = []

    if len(cls.__bases__) > 1:
        raise Exception("Structs only support single inheritance")
    for k, v in cls.__dict__.items():
        if isinstance(v, type):
            v = create_pair(k, v)
            vars.append(k)
        elif isinstance(v, tuple) and \
                isinstance(v[0], type) and \
                isinstance(v[1], v[0]):
            if len(v) == 3:
                if v[2] == NOPRINT:
                    excludes.append(k)
            v = create_pair(k, v[0], v[1])
            vars.append(k)
        elif isinstance(v, tuple) and \
                isinstance(v[0], type) and \
                v[1] == NOPRINT:
            if v == bool:
                log.warn('WARNING - bool value ambiguitiy, interpretting '
                         'as PRINT -- If you meant default, '
                         'please be explicit')
            v = create_pair(k, v[0])
            vars.append(k)
            # v = create_pair(k, v[0])

        new_cls_dict[k] = v
    new_cls_dict['__init__'] = __init__struct
    new_cls_dict['__repr__'] = __repr__ if not hasattr(cls, '__repr__') else cls.__repr__
    new_cls_dict['_vars'] = vars
    new_cls_dict['_excludes'] = excludes
    new_cls_dict['to_dict'] = to_dict if not hasattr(cls, 'to_dict') else cls.to_dict
    return type(cls)(cls.__name__, cls.__bases__, new_cls_dict)


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
    raise Exception('Exchange type not implemented : %s ' % ex)


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
        raise Exception(f'CurrencyType not recognized {s}')
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
        raise Exception(f'Exchange not recognized: {exchange}')
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
