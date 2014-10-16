import json
import logging
import os

_ROOT = os.path.abspath(os.path.dirname(__file__))

LOG_CONFIG_DEFAULT = '%s/etc/logging.json' % (_ROOT)
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s %(message)s'
LOG_DATE = '%Y-%m-%d %I:%M:%S %p'


def default(level='info', filename=None):
    try:
        load(filename)
    except:
        # silent ignore
        pass

    logging.basicConfig(format=LOG_FORMAT,
                        datefmt=LOG_DATE,
                        level=level.upper())


def load(filename):
    with open(filename, 'rt') as f:
        config = json.load(f)

        logging.config.dictConfig(config)
