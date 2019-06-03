# coding: utf8

"""
This software is licensed under the Apache 2 license, quoted below.

Copyright 2015 Crystalnix Limited

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

import os

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from feedback.serializers import FeedbackSerializer
from feedback.factories import FeedbackFactory, FeedbackDescriptionFactory

from omaha.tests.utils import temporary_media_root
from omaha.tests.test_api import BaseTest
from omaha_server.utils import is_private


class FeedbackDescriptionTest(BaseTest, APITestCase):
    url = 'api-feedback-description-list'
    url_detail = 'api-feedback-description-detail'
    factory = FeedbackDescriptionFactory
    serializer = FeedbackSerializer

    @is_private()
    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    def test_detail(self):
        super(FeedbackDescriptionTest, self).test_detail()

    @is_private()
    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    def test_list(self):
        response = self.client.get(reverse(self.url), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 10)
        self.assertEqual(self.serializer(self.objects, many=True).data, response.data['results'][::-1])

    @is_private()
    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    def test_create(self):
        response = self.client.post(reverse(self.url), {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class FeedbackTest(FeedbackDescriptionTest):
    url = 'api-feedback-list'
    url_detail = 'api-feedback-detail'
    factory = FeedbackFactory
    serializer = FeedbackSerializer

    @is_private()
    @temporary_media_root(MEDIA_URL='http://cache.pack.google.com/edgedl/chrome/install/782.112/')
    def test_detail(self):
        super(FeedbackTest, self).test_detail()
