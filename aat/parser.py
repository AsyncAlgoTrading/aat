from configparser import ConfigParser
from pydoc import locate
from .config import TradingEngineConfig, BacktestConfig, StrategyConfig
from .enums import TradingType
from .exceptions import ConfigException
from .utils import str_to_exchange, set_verbose, str_to_currency_pair_type
from .logging import LOG as log


def parse_file_config(filename: str) -> TradingEngineConfig:
    config = TradingEngineConfig()
    c = ConfigParser()
    c.read(filename)

    general = c['general']
    exchange = c['exchange']
    strategy = c['strategy']
    risk = c['risk']
    default = c['DEFAULT']

    _parse_general(general, config)
    _parse_exchange(exchange, config)
    _parse_strategy(strategy, config)
    _parse_risk(risk, config)
    _parse_default(default, config)
    return config


def _parse_general(general, config) -> None:
    if 'TradingType' in general:
        if general['TradingType'].lower() == 'live':
            set_all_trading_types(TradingType.LIVE, config)
        elif general['TradingType'].lower() == 'simulation':
            set_all_trading_types(TradingType.SIMULATION, config)
        elif general['TradingType'].lower() == 'sandbox':
            set_all_trading_types(TradingType.SANDBOX, config)
        elif general['TradingType'].lower() == 'backtest':
            set_all_trading_types(TradingType.BACKTEST, config)
        else:
            raise ConfigException('Trading type not recognized : %s',
                                  general['TradingType'])
    else:
        raise ConfigException('TradingType unspecified')

    if 'verbose' in general:
        if int(general['verbose']) >= 1:
            set_verbose(int(general['verbose']))

    if 'print' in general:
        if general['print'] == '1':
            config.print = True


def _parse_exchange(exchange, config) -> None:
    if config.type == TradingType.LIVE:
        _parse_live_options(exchange, config)

    elif config.type == TradingType.SIMULATION:
        _parse_simulation_options(exchange, config)

    elif config.type == TradingType.SANDBOX:
        _parse_sandbox_options(exchange, config)

    elif config.type == TradingType.BACKTEST:
        _parse_backtest_options(exchange, config)

    else:
        ConfigException('No Trading Type specified in config!')


def _parse_strategy(strategy, config) -> None:
    strat_configs = []
    if 'strategies' not in strategy:
        raise Exception('No Strategies specified')

    for strat in strategy['strategies'].split('\n'):
        if strat == '':
            continue
        splits = [x for x in strat.split(',') if x]
        cls = locate(splits[0])

        args = []
        for x in splits[1:]:
            args.append(float(x.strip()) if x.strip().isdigit() else x)
        args = tuple(args)

        strat_configs.append(StrategyConfig(clazz=cls, args=args))
    config.strategy_options = strat_configs


def _parse_risk(risk, config) -> None:
    config.risk_options.max_drawdown = float(risk.get('max_drawdown', config.risk_options.max_drawdown))
    config.risk_options.max_risk = float(risk.get('max_drawdown', config.risk_options.max_risk))
    config.risk_options.total_funds = float(risk.get('total_funds', config.risk_options.total_funds))


def _parse_default(default, config) -> None:
    pass


def _parse_args_to_dict(argv: list) -> dict:
    ret = {}
    for item in argv[1:]:
        if '--' not in item:
            log.critical('Argument not recognized: %s', item)
        value = item.split('--')[1]
        if '=' in value:
            # = args
            splits = value.split('=')
            ret[splits[0]] = splits[-1]
        else:
            # single args
            if value.upper() in TradingType.members():
                ret['ttype'] = value
            elif value.upper() == 'VERBOSE':
                ret['verbose'] = True
            elif value.upper() == 'PRINT':
                ret['print'] = True
            else:
                log.critical('Argument not recognized: %s', item)
    return ret


def _parse_currencies(currencies):
    splits = [x.strip().upper().replace('-', '') for x in currencies.split(',')]
    ret = []
    for s in splits:
        ret.append(str_to_currency_pair_type(s))
    return ret


def _parse_options(argv, config: TradingEngineConfig) -> None:
    if argv.get('exchanges'):
        config.exchange_options.exchange_types = [str_to_exchange(x) for x in argv['exchanges'].split() if x]
    else:
        raise Exception('No exchange set!')

    if argv.get('currency_pairs'):
        config.exchange_options.currency_pairs = _parse_currencies(argv.get('currency_pairs'))


def _parse_live_options(argv, config: TradingEngineConfig) -> None:
    log.critical("\n\nWARNING: Live trading. money will be lost ;^)\n\n")
    _parse_options(argv, config)


def _parse_simulation_options(argv, config) -> None:
    log.critical("")
    log.critical("Simulation trading")
    log.critical("")
    _parse_options(argv, config)


def _parse_sandbox_options(argv, config) -> None:
    log.critical("")
    log.critical("Sandbox trading")
    log.critical("")
    _parse_options(argv, config)


def _parse_backtest_options(argv, config) -> None:
    log.critical("")
    log.critical("Backtesting")
    log.critical("")
    config.backtest_options = BacktestConfig()

    if argv.get('exchanges'):
        config.exchange_options.exchange_types = [str_to_exchange(x) for x in argv['exchanges'].split() if x]
    else:
        raise Exception('No exchange set!')

    if argv.get('currency_pairs'):
        config.exchange_options.currency_pairs = _parse_currencies(argv.get('currency_pairs'))


def parse_command_line_config(argv: list) -> TradingEngineConfig:
    # Every engine run requires a static config object
    argv = _parse_args_to_dict(argv)

    if argv.get('config'):
        config = parse_file_config(argv.get('config'))
    else:
        config = TradingEngineConfig()

        if 'live' == argv.get('ttype'):
            # WARNING: Live trading. money will be lost ;^)
            set_all_trading_types(TradingType.LIVE, config)
            _parse_live_options(argv, config)

        elif 'sandbox' == argv.get('ttype'):
            # Trade against sandbox
            _parse_sandbox_options(argv, config)
            set_all_trading_types(TradingType.SANDBOX, config)

        elif 'backtest' == argv.get('ttype'):
            # Backtest against trade data
            set_all_trading_types(TradingType.BACKTEST, config)
            _parse_backtest_options(argv, config)
        else:
            raise ConfigException('Trading Type not specified')

        if argv.get('verbose'):
            set_verbose()

        if argv.get('print'):
            config.print = True

    log.debug("Config : %s", str(config))

    return config


def set_all_trading_types(trading_type: TradingType,
                          config: TradingEngineConfig) -> None:
    config.type = trading_type
    config.exchange_options.trading_type = trading_type
    config.risk_options.trading_type = trading_type
    config.execution_options.trading_type = trading_type
