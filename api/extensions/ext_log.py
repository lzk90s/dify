# coding: utf-8
import logging
import os.path
import sys

from flask import Flask

logger = logging.getLogger(__name__)


def is_celery_worker():
    return 'app.celery' in sys.argv and 'worker' in sys.argv


def init_app(app: Flask):
    log_home = app.config.get('LOG_HOME', 'logs')
    if not os.path.exists(log_home):
        os.mkdir(log_home)

    log_prefix = 'worker_' if is_celery_worker() else ''

    date_format = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d - %(levelname)s - [%(filename)s %(funcName)s %(lineno)s] - %(message)s', date_format)

    debug_handler = logging.FileHandler(os.path.join(log_home, f'{log_prefix}debug.log'))
    debug_handler.setLevel(logging.DEBUG)

    info_handler = logging.FileHandler(os.path.join(log_home, f'{log_prefix}info.log'))
    info_handler.setLevel(logging.INFO)

    warning_handler = logging.FileHandler(os.path.join(log_home, f'{log_prefix}warning.log'))
    warning_handler.setLevel(logging.WARNING)

    error_handler = logging.FileHandler(os.path.join(log_home, f'{log_prefix}error.log'))
    error_handler.setLevel(logging.ERROR)

    debug_handler.setFormatter(formatter)
    info_handler.setFormatter(formatter)
    warning_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)

    debug_filter = logging.Filter()
    debug_filter.filter = lambda record: record.levelno == logging.DEBUG

    info_filter = logging.Filter()
    info_filter.filter = lambda record: record.levelno == logging.INFO

    warning_filter = logging.Filter()
    warning_filter.filter = lambda record: record.levelno == logging.WARNING

    error_filter = logging.Filter()
    error_filter.filter = lambda record: record.levelno == logging.ERROR

    debug_handler.addFilter(debug_filter)
    info_handler.addFilter(info_filter)
    warning_handler.addFilter(warning_filter)
    error_handler.addFilter(error_filter)

    logging.root.setLevel(app.config.get('LOG_LEVEL', 'INFO'))
    logging.root.addHandler(debug_handler)
    logging.root.addHandler(info_handler)
    logging.root.addHandler(warning_handler)
    logging.root.addHandler(error_handler)
