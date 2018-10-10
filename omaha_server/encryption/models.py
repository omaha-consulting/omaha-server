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
from logging import getLogger
from django_extensions.db.fields import (
    CreationDateTimeField, ModificationDateTimeField,
)

from django.db import models

from .utils import generate_rsa_keys
from .key_storages import get_key_storage_class

logger = getLogger(__name__)

STORAGE_CHOICES = (
        ('db', 'Database'),
        ('custom', 'Custom'),
)


class GeneratedKey(models.Model):
    created = CreationDateTimeField('created')
    type = models.CharField(choices=STORAGE_CHOICES, max_length=32)
    is_enabled = models.BooleanField(default=True)
    private_key = models.TextField(blank=True)
    public_key = models.TextField(blank=True)

    @classmethod
    def generate(cls, is_enabled=True):
        """Generate a new key."""
        key = cls(is_enabled=is_enabled)
        public, private = generate_rsa_keys()
        storage = get_key_storage_class()()
        storage.save_keys(key, private_key=private, public_key=public)
        return key

    def get_public_key(self):
        storage = get_key_storage_class()()
        return storage.get_public_key(self)

    def get_private_key(self):
        storage = get_key_storage_class()()
        return storage.get_private_key(self)


class DecryptionData(models.Model):
    key_id = models.TextField()
    is_decrypted = models.BooleanField(default=False)
    encrypted_aes_key = models.TextField()
    created = CreationDateTimeField('created')
    modified = ModificationDateTimeField('modified')

    @classmethod
    def create_from_headers(cls, headers):
        aes_key = headers.get('HTTP_X_AES_KEY', '')
        key_id = headers.get('HTTP_X_KEY_ID', '')
        if not aes_key or not key_id:
            logger.warning('X-AES_KEY and X-KEY-ID headers are required')
            return
        data = cls(key_id=key_id, encrypted_aes_key=aes_key)
        data.save()
        return data
