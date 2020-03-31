import importlib
import os
import os.path
from configparser import ConfigParser
from typing import List


def _config_to_dict(filename: str) -> dict:
    if not os.path.exists(filename):
        raise Exception(f'File does not exist {filename}')
    config = ConfigParser()
    config.read(filename)

    ret = {}
    for s in config.sections():
        d = dict(config.items(s))
        for k, v in d.items():
            if v.startswith('\n'):
                d[k] = v.strip().split('\n')
            elif ',' in v:
                d[k] = v.strip().split(',')
        ret[s] = d
    return ret


def getStrategies(strategies: List) -> List:
    strategy_instances = []
    for strategy in strategies:
        mod, clazz_and_args = strategy.split(':')
        clazz, args = clazz_and_args.split(',') if ',' in clazz_and_args else clazz_and_args, ()
        mod = importlib.import_module(mod)
        clazz = getattr(mod, clazz)
        strategy_instances.append(clazz(*args))
    return strategy_instances


def parseConfig(argv: list) -> dict:
    # Every engine run requires a static config object
    if len(argv) != 2:
        print('usage: <python executable> -m aat <config file>')
        raise Exception(f'Invalid command line: {argv}')
    return _config_to_dict(argv[-1])
