""" Console and File Logging Functions """
import os
import sys
import logging

import config

LOGGER_NAME = "ModelTrader"
FMT = '{asctime} :: {message}'

DATE_FMT = '%m/%d/%Y %I:%M:%S %p'
#DATE_FMT = '%d %I:%M %p'


def setup():
    if os.path.exists(config.LOGFILE):
        os.remove(config.LOGFILE)

    handlers = [
        logging.StreamHandler(stream=sys.stdout)
    ]

    if config.LOGFILE_ENABLED:
        handlers.append(logging.FileHandler(filename=config.LOGFILE))

    logger = logging.getLogger(LOGGER_NAME)
    #logger.setLevel(logging.INFO)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    for handler in handlers:
        handler.setFormatter(logging.Formatter(fmt=FMT, datefmt=DATE_FMT, style='{'))
        logger.addHandler(handler)


def getLogger():
    return logging.getLogger(LOGGER_NAME)
