import base64
from builtins import bytes, range
import json
from collections import defaultdict

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connections

from omaha_server.utils import is_private
from omaha.factories import VersionFactory, ApplicationFactory, ChannelFactory
from sparkle.factories import SparkleVersionFactory


User = get_user_model()

class DownloadsTest(APITestCase):
    maxDiff = None

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='secret', email='test@example.com')
        self.client.credentials(
            HTTP_AUTHORIZATION='Basic %s' % base64.b64encode(bytes('{}:{}'.format('test', 'secret'), 'utf8')).decode())

        self.app = ApplicationFactory(name='TestApp')
        self.channel = ChannelFactory(name='alpha')
        self.stable_channel = ChannelFactory(name='stable')
        self.win_v1 = VersionFactory(version='10.0.0.0', app=self.app, channel=self.channel)
        self.win_v2 = VersionFactory(version='42.0.1.0', app=self.app, channel=self.channel)
        self.win_stable_v = VersionFactory(version='23.0.0.0', app=self.app, channel=self.stable_channel)
        self.win_disabled_v = VersionFactory(version='55.0.2.0', app=self.app, channel=self.channel, is_enabled=False)

        self.mac_v1 = SparkleVersionFactory(short_version='10.0.0.0', version='0.0',
                                            app=self.app, channel=self.channel)
        self.mac_v2 = SparkleVersionFactory(short_version='42.0.1.0', version='1.0',
                                            app=self.app, channel=self.channel)
        self.mac_stable_v = SparkleVersionFactory(short_version='23.0.0.0', version='0.0',
                                                  app=self.app, channel=self.stable_channel)
        self.mac_disabled_v = SparkleVersionFactory(short_version='55.0.2.0', version='2.0',
                                                    app=self.app, channel=self.channel, is_enabled=False)
        self.exp_res = {
            self.app.name: {
                "win": {
                    self.channel.name: {
                        "url": self.win_v2.file_absolute_url,
                        "version": self.win_v2.version
                    },
                    self.stable_channel.name: {
                        "url": self.win_stable_v.file_absolute_url,
                        "version": self.win_stable_v.version
                    }
                },
                "mac": {
                    self.channel.name: {
                        "url": self.mac_v2.file_absolute_url,
                        "version": self.mac_v2.short_version
                    },
                    self.stable_channel.name: {
                        "url": self.mac_stable_v.file_absolute_url,
                        "version": self.mac_stable_v.short_version
                    }
                }
            }
        }

    @is_private()
    def test_unauthorized(self):
        client = APIClient()
        response = client.get('/api/downloads', format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test(self):
        if connections['default'].settings_dict['ENGINE'] != 'django.db.backends.postgresql_psycopg2':
            self.skipTest('Database should be postgreSQL')
        response = self.client.get('/api/downloads', format='json')

        self.assertEqual(json.loads(json.dumps(response.data)), self.exp_res)
