# coding: utf8

__all__ = ['get_sec_since_midnight']


def get_sec_since_midnight(date):
    """
    Return seconds since midnight

    >>> from datetime import datetime
    >>> get_sec_since_midnight(datetime(year=2014, month=1, day=1, second=42))
    42
    """
    midnight = date.replace(hour=0, minute=0, second=0, microsecond=0)
    delta = date - midnight
    return delta.seconds
