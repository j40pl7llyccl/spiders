import os
from logging.config import dictConfig

ROOT_PATH = os.path.abspath(os.curdir)
LOG_DIR = os.path.join(ROOT_PATH, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': { 'format': '[%(levelname)s][%(asctime)s][%(name)s]: %(message)s'},
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'standard',
            'filename': os.path.join(LOG_DIR, 'main.log'),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 5,
            'encoding': "utf-8",
        },
        'wms': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'standard',
            'filename': os.path.join(LOG_DIR, 'wms.log'),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 5,
            'encoding': "utf-8",
        },
        'chrome': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'standard',
            'filename': os.path.join(LOG_DIR, 'chrome.log'),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 5,
            'encoding': "utf-8",
        },
    },
    'loggers': {
        'wms': {
            'handlers': ['wms'],
            'level': 'DEBUG',
            'propagate': False
        },
        '__main__': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
dictConfig(DEFAULT_LOGGING)