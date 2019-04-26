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

from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework import status
from rest_framework.test import APITestCase

from omaha.factories import ApplicationFactory, ChannelFactory

from sparkle.serializers import SparkleVersionSerializer
from sparkle.factories import SparkleVersionFactory
from sparkle.models import SparkleVersion

from omaha.tests.utils import temporary_media_root
from omaha.tests import OverloadTestStorageMixin
from omaha.tests.test_api import BaseTest
from omaha_server.utils import is_private


class VersionTest(OverloadTestStorageMixin, BaseTest, APITestCase):
    url = 'sparkleversion-list'
    url_detail = 'sparkleversion-detail'
    factory = SparkleVersionFactory
    serializer = SparkleVersionSerializer
    model = SparkleVersion

    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    def setUp(self):
        super(VersionTest, self).setUp()

    @is_private()
    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    def test_detail(self):
        super(VersionTest, self).test_detail()

    @is_private()
    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    def test_list(self):
        super(VersionTest, self).test_list()

    @is_private()
    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    def test_create(self):
        data = dict(
            app=ApplicationFactory.create().id,
            channel=ChannelFactory.create().id,
            version='3.4',
            file=SimpleUploadedFile("chrome.exe", b'content'),
        )
        response = self.client.post(reverse(self.url), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        version = SparkleVersion.objects.get(id=response.data['id'])
        self.assertEqual(response.data, self.serializer(version).data)
        self.assertEqual(version.file_size, len(b'content'))
        self.assertTrue(version.is_enabled)

    @is_private()
    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    def test_update(self):
        data = dict(
            app=ApplicationFactory.create().id,
            channel=ChannelFactory.create().id,
            version='3.4',
            file=SimpleUploadedFile("chrome.exe", b'content'),
        )
        response = self.client.post(reverse(self.url), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        obj_id = response.data['id']
        version = SparkleVersion.objects.get(id=obj_id)
        self.assertEqual(version.version, '3.4')
        url = reverse(self.url_detail, kwargs=dict(pk=obj_id))
        response = self.client.patch(url, dict(version='3.5'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        version = SparkleVersion.objects.get(id=obj_id)
        self.assertEqual(version.version, '3.5')
