""" utility, minimal logging   """
import logging


def default_logging(loglevel):
    """ bare bones logging"""
    fmt = '%(asctime)s - %(levelname)s - %(threadName)s - %(message)s'
    logging.basicConfig(level=loglevel, format=fmt)
