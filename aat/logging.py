import os
import os.path
import logging.config
import time

moment = time.strftime("%Y%m%d_%H%M%S", time.localtime())

if not os.path.isdir('./logs'):
    os.mkdir('./logs')

if not os.path.isdir('./logs' + moment):
    os.mkdir('./logs/' + moment)


LOGGING_CONFIG = {
    'version': 1,  # required
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s %(levelname)s -- %(message)s'
        },
        'whenAndWhere': {
            'format': '%(asctime)s\t%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'whenAndWhere'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'whenAndWhere',
            'filename': 'logs/' + moment + '/out.log',
            'mode': 'w',
            'encoding': 'utf-8'
        },
        'file_strat': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'whenAndWhere',
            'filename': 'logs/' + moment + '/strat.log',
            'mode': 'w',
            'encoding': 'utf-8'
        },

        'file_data': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'whenAndWhere',
            'filename': 'logs/' + moment + '/data.log',
            'mode': 'w',
            'encoding': 'utf-8'
        },
        'file_risk': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'whenAndWhere',
            'filename': 'logs/' + moment + '/risk.log',
            'mode': 'w',
            'encoding': 'utf-8'
        },
        'file_execution': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'whenAndWhere',
            'filename': 'logs/' + moment + '/exec.log',
            'mode': 'w',
            'encoding': 'utf-8'
        },
        'file_slippage': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'whenAndWhere',
            'filename': 'logs/' + moment + '/slip.log',
            'mode': 'w',
            'encoding': 'utf-8'
        },
        'file_transaction_costs': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'whenAndWhere',
            'filename': 'logs/' + moment + '/txns.log',
            'mode': 'w',
            'encoding': 'utf-8'
        },
        'file_manual': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'whenAndWhere',
            'filename': 'logs/' + moment + '/manual.log',
            'mode': 'w',
            'encoding': 'utf-8'
        },
        'file_errors': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'whenAndWhere',
            'filename': 'logs/' + moment + '/errors.log',
            'mode': 'w',
            'encoding': 'utf-8'
        },
    },
    'loggers': {
        '': {  # 'root' logger
            'level': 'CRITICAL',
            'handlers': ['console', 'file']
        },
        'strat': {
            'level': 'CRITICAL',
            'handlers': ['console', 'file_strat']
        },
        'data': {
            'level': 'CRITICAL',
            'handlers': ['console', 'file_data']
        },
        'risk': {
            'level': 'CRITICAL',
            'handlers': ['console', 'file_risk']
        },
        'execution': {
            'level': 'CRITICAL',
            'handlers': ['console', 'file_execution']
        },
        'slippage': {
            'level': 'CRITICAL',
            'handlers': ['console', 'file_slippage']
        },
        'transactionCost': {
            'level': 'CRITICAL',
            'handlers': ['console', 'file_transaction_costs']
        },
        'manual': {
            'level': 'CRITICAL',
            'handlers': ['console', 'file_manual']
        },
        'errors': {
            'level': 'CRITICAL',
            'handlers': ['console', 'file_errors']
        },

    }
}

logging.config.dictConfig(LOGGING_CONFIG)
LOG = logging.getLogger('')  # factory method
STRAT = logging.getLogger('strat')
DATA = logging.getLogger('data')
RISK = logging.getLogger('risk')
EXEC = logging.getLogger('execution')
SLIP = logging.getLogger('slippage')
TXNS = logging.getLogger('transactionCost')
MANUAL = logging.getLogger('manual')
ERROR = logging.getLogger('errors')

STRAT.propagate = False
DATA.propagate = False
RISK.propagate = False
EXEC.propagate = False
SLIP.propagate = False
TXNS.propagate = False
MANUAL.propagate = False
ERROR.propagate = False

STRAT.setLevel(logging.CRITICAL)
DATA.setLevel(logging.CRITICAL)
RISK.setLevel(logging.CRITICAL)
EXEC.setLevel(logging.CRITICAL)
SLIP.setLevel(logging.CRITICAL)
TXNS.setLevel(logging.CRITICAL)
MANUAL.setLevel(logging.CRITICAL)
ERROR.setLevel(logging.CRITICAL)
