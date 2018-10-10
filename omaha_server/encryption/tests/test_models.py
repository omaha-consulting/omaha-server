from django.test import TestCase

from ..factories import GeneratedKeyFactory
from ..models import GeneratedKey, DecryptionData


class GeneratedKeyTest(TestCase):
    def test_generate_key_pair(self):
        is_enabled = False
        key = GeneratedKey.generate(is_enabled=is_enabled)
        assert key.private_key.startswith('-----BEGIN PRIVATE KEY-----')
        assert key.public_key.startswith('-----BEGIN PUBLIC KEY-----')


class DecryprionDataTest(TestCase):
    def test_create_from_headers(self):
        key = GeneratedKeyFactory.create()
        headers = {'HTTP_X_ID_KEY': key.pk, 'HTTP_X_AES_KEY': 'encrypted'}
        data = DecryptionData.create_from_headers(headers)
        assert data.key.pk == headers['HTTP_X_ID_KEY']
        assert data.encrypted_aes_key == headers['HTTP_X_AES_KEY']
