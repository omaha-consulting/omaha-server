# coding: utf8

"""
This software is licensed under the Apache 2 license, quoted below.

Copyright 2014 Crystalnix Limited

Licensed under the Apache License, Version 2.0 (the "License"); you may not
use this file except in compliance with the License. You may obtain a copy of
the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations under
the License.
"""
import abc
import base64

class BaseStorage(object):
    """Base class to implement different storages for generated keys."""
    storage_name = None
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_public_key(self, generated_key):
        pass

    @abc.abstractmethod
    def get_private_key(self, generated_key):
        pass

    @abc.abstractmethod
    def save_keys(self, cls, private_key, public_key):
        pass


class DatabaseStorage(BaseStorage):
    """Store keys in DB."""
    storage_name = 'db'

    def get_public_key(self, generated_key):
        return generated_key.public_key

    def get_private_key(self, generated_key):
        return generated_key.private_key

    def save_keys(self, key_instance, private_key, public_key):
        key_instance.private_key = private_key
        key_instance.public_key = public_key
        key_instance.type = self.storage_name
        return key_instance.save()


STORAGE_MAPPING = {
    'db': DatabaseStorage
}


def get_key_storage_class(storage_type=None):
    """Get key storage class."""
    from omaha.dynamic_preferences_registry import global_preferences_manager as gpm

    if not storage_type:
        storage_type = gpm['Encryption__key_storage']
    return STORAGE_MAPPING[storage_type]
