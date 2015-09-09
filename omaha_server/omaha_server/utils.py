# coding: utf8

from functools import wraps
from django.conf import settings


class is_private(object):
    def __init__(self, is_private=True):
        self.is_private = is_private

    def __call__(self, test_func):
        @wraps(test_func)
        def inner(*args, **kwargs):
            if not self.is_private and not settings.IS_PRIVATE:
                return test_func(*args, **kwargs)
            elif not self.is_private and settings.IS_PRIVATE:
                return test_func(*args, **kwargs)
            elif self.is_private and settings.IS_PRIVATE:
                return test_func(*args, **kwargs)
            else:
                return

        return inner


def show_toolbar(request):
    """
    Default function to determine whether to show the toolbar on a given page.
    """

    if request.is_ajax():
        return False

    return bool(settings.DEBUG)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
