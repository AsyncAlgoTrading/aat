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
    },
    'loggers': {
        '': {  # 'root' logger
            'level': 'CRITICAL',
            'handlers': ['console', 'file']
        },
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
log = logging.getLogger('')  # factory method
