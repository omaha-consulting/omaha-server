import io
import tarfile

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import Client

from ..factories import GeneratedKeyFactory

User = get_user_model()


class GeneratedKeyAdminTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser(
            username='test', email='test@example.com', password='test')
        self.client.login(username='test', password='test')

    def test_disable_action(self):
        key = GeneratedKeyFactory.create()
        data = dict(action='disable', _selected_action=[key.pk])
        url = '/admin/encryption/generatedkey/'
        assert key.is_enabled
        self.client.post(url, data)
        key.refresh_from_db()
        assert not key.is_enabled

    def test_enable_action(self):
        key = GeneratedKeyFactory.create(is_enabled=False)
        data = dict(action='enable', _selected_action=[key.pk])
        url = '/admin/encryption/generatedkey/'
        assert not key.is_enabled
        self.client.post(url, data)
        key.refresh_from_db()
        assert key.is_enabled

    def test_export(self):
        key = GeneratedKeyFactory.create()
        data = dict(action='export', _selected_action=[key.pk])
        url = '/admin/encryption/generatedkey/'
        resp = self.client.post(url, data)
        data = io.BytesIO(resp.content)
        t_file = tarfile.TarFile(fileobj=data)
        assert set(t_file.getnames()) == {'%s.pub' % key.pk, '%s.key' % key.pk}
        assert t_file.extractfile('%s.pub' % key.pk).read() == key.public_key
        assert t_file.extractfile('%s.key' % key.pk).read() == key.private_key
