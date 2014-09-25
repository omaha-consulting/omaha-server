# coding: utf8

__all__ = ['get_sec_since_midnight']


def get_sec_since_midnight(date):
    midnight = date.replace(hour=0, minute=0, second=0, microsecond=0)
    delta = date - midnight
    return delta.seconds