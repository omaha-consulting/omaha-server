# coding: utf8

from functools import wraps
from django.core.files.storage import DefaultStorage

from django.conf import settings

import requests

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


# Link the message and extras into a '|' separated list.
def add_extra_to_log_message(msg, extra):
    return msg + '|' + '|'.join("%s=%s" % (key, val) for (key, val) in sorted(extra.items()))


def get_splunk_url(params):
    SEARCH_TEMPLATE = 'http://%s/en-US/app/search/search?q=search %s'
    FILEBEAT_HOST = getattr(settings, 'FILEBEAT_HOST', None)
    string_params = ' '.join("%s=%s" % (key, val) for (key, val) in sorted(params.items()))
    return SEARCH_TEMPLATE % (FILEBEAT_HOST, string_params) if FILEBEAT_HOST else None


def get_sentry_organization_slug(domain, api_key):  # 1 api_key - 1 organization_slug
    organizations = requests.get(
        'http://%s/api/0/organizations/' % (domain,),
        auth=(api_key, '')
    ).json()

    return organizations[0]['slug']


def get_sentry_project_slug(domain, organization, project_id, api_key):
    projects = requests.get(
        'http://%s/api/0/organizations/%s/projects/' % (domain, organization),
        auth=(api_key, '')
    ).json()

    projects = [x for x in projects if x['id'] == project_id]

    return projects[0]['slug']


class StorageWithSpaces(DefaultStorage):
    def get_valid_name(self, name):
        return name

storage_with_spaces_instance = StorageWithSpaces()
