# coding: utf8

from django.conf import settings


def show_toolbar(request):
    """
    Default function to determine whether to show the toolbar on a given page.
    """

    if request.is_ajax():
        return False

    return bool(settings.DEBUG)