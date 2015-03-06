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

from datetime import datetime
from uuid import UUID
from bitmapist import mark_event

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from omaha.tests.utils import temporary_media_root

from omaha.factories import VersionFactory
from omaha.builder import get_version
from omaha.models import PartialUpdate, Version, Channel, ACTIVE_USERS_DICT_CHOICES
from omaha.utils import redis, get_id


@temporary_media_root()
class BuilderTest(TestCase):
    def setUp(self):
        redis.flushdb()

    def tearDown(self):
        redis.flushdb()

    def test_get_version(self):
        userid = '{D0BBD725-742D-44ae-8D46-0231E881D58E}'
        version = VersionFactory.create(file=SimpleUploadedFile('./chrome_installer.exe', b''))

        self.assertEqual(version, get_version(version.app.pk,
                                              version.platform.name,
                                              version.channel.name,
                                              '36.0.2062.124',
                                              userid))

        self.assertEqual(version, get_version(version.app.pk,
                                              version.platform.name,
                                              version.channel.name,
                                              '',
                                              userid))

    def test_get_version_partial_update(self):
        userid = "{%s}" % UUID(int=1)
        userid_beta = "{%s}" % UUID(int=40)
        version = VersionFactory.create(file=SimpleUploadedFile('./chrome_installer.exe', b''))
        version_beta = Version.objects.create(
            file=SimpleUploadedFile('./chrome_installer.exe', b''),
            app=version.app,
            platform=version.platform,
            channel=version.channel,
            version='39.0.0.0',
        )

        PartialUpdate.objects.create(version=version_beta,
                                     percent=5,
                                     start_date=datetime.now(),
                                     end_date=datetime.now(),
                                     active_users=ACTIVE_USERS_DICT_CHOICES['all'])

        self.assertEqual(version, get_version(version.app.pk,
                                              version.platform.name,
                                              version.channel.name,
                                              '36.0.2062.124',
                                              userid))

        self.assertEqual(version_beta, get_version(version.app.pk,
                                                   version.platform.name,
                                                   version.channel.name,
                                                   '36.0.2062.124',
                                                   userid_beta))

    def test_get_app_version_channel(self):
        userid = '{D0BBD725-742D-44ae-8D46-0231E881D58E}'
        channel_beta = Channel.objects.create(name="beta")
        version = VersionFactory.create(file=SimpleUploadedFile('./chrome_installer.exe', b''))
        version_beta = Version.objects.create(
            file=SimpleUploadedFile('./chrome_installer.exe', b''),
            app=version.app,
            platform=version.platform,
            channel=channel_beta,
            version='39.0.0.0',
        )

        self.assertEqual(version_beta, get_version(version.app.pk,
                                              version.platform.name,
                                              channel_beta.name,
                                              '',
                                              userid))

    def test_get_app_version_exlude_new_users(self):
        userid = "{%s}" % UUID(int=1)
        userid_beta = "{%s}" % UUID(int=40)
        version = VersionFactory.create(file=SimpleUploadedFile('./chrome_installer.exe', b''))
        version_beta = Version.objects.create(
            file=SimpleUploadedFile('./chrome_installer.exe', b''),
            app=version.app,
            platform=version.platform,
            channel=version.channel,
            version='39.0.0.0',
        )

        PartialUpdate.objects.create(version=version_beta,
                                     percent=5,
                                     start_date=datetime.now(),
                                     end_date=datetime.now(),
                                     active_users=ACTIVE_USERS_DICT_CHOICES['all'])

        self.assertEqual(version, get_version(version.app.pk,
                                              version.platform.name,
                                              version.channel.name,
                                              '36.0.2062.124',
                                              userid))

        self.assertEqual(version_beta, get_version(version.app.pk,
                                                   version.platform.name,
                                                   version.channel.name,
                                                   '36.0.2062.124',
                                                   userid_beta))

        self.assertEqual(version, get_version(version.app.pk,
                                              version.platform.name,
                                              version.channel.name,
                                              '',
                                              userid_beta))

    def test_get_app_version_active_users(self):
        userid = "{%s}" % UUID(int=1)
        userid_beta = "{%s}" % UUID(int=40)
        userid_beta_not_active = "{%s}" % UUID(int=60)
        version = VersionFactory.create(file=SimpleUploadedFile('./chrome_installer.exe', b''))
        version_beta = Version.objects.create(
            file=SimpleUploadedFile('./chrome_installer.exe', b''),
            app=version.app,
            platform=version.platform,
            channel=version.channel,
            version='39.0.0.0',
        )


        id = get_id(userid_beta)
        mark_event('request', id)

        PartialUpdate.objects.create(version=version_beta,
                                     percent=5,
                                     start_date=datetime.now(),
                                     end_date=datetime.now())

        self.assertEqual(version, get_version(version.app.pk,
                                              version.platform.name,
                                              version.channel.name,
                                              '36.0.2062.124',
                                              userid))

        self.assertEqual(version_beta, get_version(version.app.pk,
                                                   version.platform.name,
                                                   version.channel.name,
                                                   '36.0.2062.124',
                                                   userid_beta))

        self.assertEqual(version, get_version(version.app.pk,
                                              version.platform.name,
                                              version.channel.name,
                                              '36.0.2062.124',
                                              userid_beta_not_active))
