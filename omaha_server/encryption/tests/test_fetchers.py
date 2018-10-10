from django.test import TestCase

from ..factories import GeneratedKeyFactory
from ..fetchers import DefaultKeyFetcher


class DefaultFetcherTest(TestCase):
    def setUp(self):
        self.keys = GeneratedKeyFactory.create_batch(2)
        self.fetcher = DefaultKeyFetcher()

    def test_get_latest_public_key(self):
        latest_key = self.keys[-1]
        resp = self.fetcher.get_latest_public_key()
        assert resp == {
            'id': latest_key.id,
            'key': latest_key.public_key
        }

    def test_get_private_key(self):
        first_key = self.keys[0]
        key = self.fetcher.get_private_key(first_key.id)
        assert key == first_key.private_key
