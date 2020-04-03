import importlib
import os
import os.path
from configparser import ConfigParser
from typing import List, Dict, Union


def _config_to_dict(filename: str) -> Dict[str, Dict[str, Union[str, List[str]]]]:
    if not os.path.exists(filename):
        raise Exception(f'File does not exist {filename}')
    config = ConfigParser()
    config.read(filename)

    ret: Dict[str, Dict[str, Union[str, List[str]]]] = {}

    for s in config.sections():
        d: Dict[str, str] = dict(config.items(s))
        ret[s] = {}
        for k, v in d.items():
            if v.startswith('\n'):
                ret[s][k] = v.strip().split('\n')
            elif ',' in v:
                ret[s][k] = v.strip().split(',')
            else:
                ret[s][k] = v
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
