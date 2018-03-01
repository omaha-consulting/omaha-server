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

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from omaha.tests.utils import temporary_media_root
from omaha.models import Version
from omaha.factories import ApplicationFactory, DataFactory, PlatformFactory, ChannelFactory, VersionFactory, ActionFactory, PartialUpdateFactory
from omaha.serializers import AppSerializer, DataSerializer, PlatformSerializer, ChannelSerializer, VersionSerializer, ActionSerializer, PartialUpdateSerializer
from datetime import date


class PartialUpdateSerializerTest(TestCase):
    def test_serializer(self):
        today = date.today()
        version = VersionFactory()
        data = dict(
            is_enabled=True,
            exclude_new_users=True,
            version=version,
            end_date=str(date(today.year, today.month, today.day)),
            percent=51.0,
            start_date=str(date(today.year, today.month, today.day)),
            active_users=1,
        )
        partial = PartialUpdateFactory(**data)
        self.assertDictEqual(
            PartialUpdateSerializer(partial).data,
            dict(
                id=partial.pk,
                is_enabled=partial.is_enabled,
                exclude_new_users=partial.exclude_new_users,
                version=partial.version.pk,
                end_date=partial.end_date,
                percent=partial.percent,
                start_date=partial.start_date,
                active_users=partial.active_users,
            )
        )


class AppSerializerTest(TestCase):
    def test_serializer(self):
        data = dict(id='{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}',
                    name='chrome2')
        app = ApplicationFactory(**data)
        data.update(dict(data_set=[]))
        self.assertDictEqual(AppSerializer(app).data, data)


class PlatformSerializerTest(TestCase):
    def test_serializer(self):
        data = dict(name='win')
        platform = PlatformFactory(**data)
        self.assertDictEqual(PlatformSerializer(platform).data, dict(id=platform.pk, **data))


class ChannelSerializerTest(TestCase):
    def test_serializer(self):
        data = dict(name='stable')
        channel = ChannelFactory(**data)
        self.assertDictEqual(ChannelSerializer(channel).data, dict(id=channel.pk, **data))


class ActionSerializerTest(TestCase):
    def test_serializer(self):
        data = dict(terminateallbrowsers=True)
        action = ActionFactory(**data)
        self.assertDictEqual(ActionSerializer(action).data,
                             dict(id=action.pk,
                                  successsaction=action.successsaction,
                                  run=action.run,
                                  event=action.event,
                                  other=action.other,
                                  version=action.version.pk,
                                  successurl=action.successurl,
                                  arguments=action.arguments,
                                  **data))


class DataSerializerTest(TestCase):
    def test_serializer(self):
        _data = DataFactory()
        self.assertDictEqual(DataSerializer(_data).data,
                             dict(id=_data.pk,
                                  app=_data.app.pk,
                                  name=_data.name,
                                  index=_data.index,
                                  value=_data.value,
                                  ))


class VersionSerializerTest(TestCase):
    maxDiff = None

    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    def test_serializer(self):
        version = VersionFactory.create(file=SimpleUploadedFile('./chrome_installer.exe', False))
        self.assertDictEqual(VersionSerializer(version).data, dict(
            id=version.id,
            is_enabled=version.is_enabled,
            is_critical=version.is_critical,
            app=version.app.id,
            platform=version.platform.id,
            channel=version.channel.id,
            version=str(version.version),
            release_notes=version.release_notes,
            file=version.file.url,
            file_hash=version.file_hash,
            file_size=version.file_size,
            created=version.created.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            modified=version.modified.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        ))

    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    def test_auto_fill_file_size(self):
        version = VersionFactory.create(file=SimpleUploadedFile('./chrome_installer.exe', b' ' * 10))
        data = dict(
            app=version.app.id,
            platform=version.platform.id,
            channel=version.channel.id,
            version='4.3.2.1',
            release_notes=version.release_notes,
            file=version.file,
            file_hash=version.file_hash,
        )

        new_version = VersionSerializer(data=data)
        self.assertTrue(new_version.is_valid())
        new_version_instance = new_version.save()
        self.assertEqual(new_version_instance.file_size, 10)
