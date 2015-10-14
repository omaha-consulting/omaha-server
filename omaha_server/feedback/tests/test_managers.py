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

from feedback.models import Feedback
from feedback.factories import FeedbackFactory


class FeedbackManagerTest(TestCase):
    def test_get_size(self):
        screenshot_size = 10
        blackbox_size = 20
        attached_file_size = 30
        system_logs_size = 40
        FeedbackFactory.create_batch(10, screenshot_size=screenshot_size,
                                     blackbox_size=blackbox_size,
                                     attached_file_size=attached_file_size,
                                     system_logs_size=system_logs_size)
        size = Feedback.objects.get_size()
        self.assertEqual(size, (screenshot_size + blackbox_size + attached_file_size + system_logs_size) * 10)

