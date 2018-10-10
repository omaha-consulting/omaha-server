import abc
import importlib

from django.conf import settings

from .models import GeneratedKey
from omaha.dynamic_preferences_registry import global_preferences_manager as gpm

class BaseKeyFetcher:
    """Inheritance from this class allows to implement a custom RSA keys storage."""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_latest_public_key(self):
        pass

    @abc.abstractmethod
    def get_private_key(self, key_id):
        pass


class DefaultKeyFetcher(BaseKeyFetcher):

    def get_latest_public_key(self):
        storage_type = gpm['Encryption__key_storage']
        key_qs = GeneratedKey.objects.filter(is_enabled=True, type=storage_type)
        key = key_qs.latest('created')
        return {
            'id': str(key.id),
            'key': key.get_public_key()
        }

    def get_private_key(self, key_id):
        key = GeneratedKey.objects.get(pk=key_id)
        return str(key.get_private_key())


def get_fetcher():
    fetcher_class = settings.ENCRYPTION_FETCHER_CLASS
    module_name, class_name = fetcher_class.rsplit(".", 1)
    return getattr(importlib.import_module(module_name), class_name)()
