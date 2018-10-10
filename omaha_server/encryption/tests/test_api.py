from rest_framework.test import APIClient, APITestCase

from ..factories import GeneratedKeyFactory


class EncryptionTest(APITestCase):
    def test_get_latest_public_key(self):
        keys = GeneratedKeyFactory.create_batch(3)
        disabled_key = keys[-1]
        disabled_key.is_enabled = False
        disabled_key.save()
        other_storage_key = keys[-2]
        other_storage_key.type = 'vault'
        other_storage_key.save()
        enabled_key = keys[-3]

        client = APIClient()
        url = '/api/latest_public_key'
        resp = client.get(url)
        assert resp.json() == {'id': enabled_key.pk, 'key': enabled_key.public_key}

    def test_no_keys(self):
        client = APIClient()
        url = '/api/latest_public_key'
        resp = client.get(url)
        assert resp.status_code == 404
        assert resp.data == 'Key Not Found'
