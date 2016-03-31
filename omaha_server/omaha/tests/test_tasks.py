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

import uuid

from django.test import TestCase

from mock import patch
from freezegun import freeze_time

from crash.models import Crash, Symbols
from crash.factories import CrashFactory, SymbolsFactory
from feedback.models import Feedback
from feedback.factories import FeedbackFactory
from omaha.dynamic_preferences_registry import global_preferences_manager as gpm
from omaha_server.utils import is_private
from omaha.models import Version
from omaha.factories import VersionFactory
from omaha.tasks import (
    auto_delete_duplicate_crashes,
    auto_delete_older_than,
    auto_delete_size_is_exceeded,
    deferred_manual_cleanup
)
from omaha_server.utils import add_extra_to_log_message
from sparkle.models import SparkleVersion
from sparkle.factories import SparkleVersionFactory

class DuplicatedCrashesTest(TestCase):
    @freeze_time("2012-12-21 12:00:00")
    @patch('logging.getLogger')
    @is_private()
    def test_crashes(self, mocked_get_logger):
        gpm['Crash__duplicate_number'] = 2
        crashes = CrashFactory.create_batch(10, signature='test')
        deleted_crash = crashes[7]
        self.assertEqual(Crash.objects.all().count(), 10)

        extra_meta = dict(count=8, reason='duplicated', meta=True, log_id='36446dc3-ae7c-42ad-ae4e-6a826dcf0a00',
                          model='Crash', size='0 bytes')
        log_extra_msg = add_extra_to_log_message('Automatic cleanup', extra=extra_meta)

        extra = dict(id=deleted_crash.id, element_created=deleted_crash.created.strftime("%d. %B %Y %I:%M%p"),
                     signature=deleted_crash.signature, userid=deleted_crash.userid, appid=deleted_crash.appid,
                     log_id='36446dc3-ae7c-42ad-ae4e-6a826dcf0a00')
        log_msg = add_extra_to_log_message('Automatic cleanup element', extra=extra)

        mocked_logger = mocked_get_logger.return_value
        with patch('uuid.uuid4') as mocked_uuid4:
            mocked_uuid4.side_effect = (uuid.UUID('36446dc3-ae7c-42ad-ae4e-6a826dcf0a%02d' % x) for x in range(100))
            auto_delete_duplicate_crashes()

        self.assertEqual(mocked_logger.info.call_count, 10)
        mocked_logger.info.assert_any_call(log_extra_msg)
        mocked_logger.info.assert_any_call(log_msg)


class OldObjectsTest(TestCase):
    @patch('logging.getLogger')
    @is_private()
    def test_crashes(self, mocked_get_logger):
        gpm['Crash__limit_storage_days'] = 2
        with freeze_time("2012-12-21 12:00:00"):
            crashes = CrashFactory.create_batch(10, signature='test')
        deleted_crash = crashes[-1]
        self.assertEqual(Crash.objects.all().count(), 10)

        extra_meta = dict(count=10, reason='old', meta=True, log_id='36446dc3-ae7c-42ad-ae4e-6a826dcf0a00',
                          model='Crash', size='0 bytes')
        log_extra_msg = add_extra_to_log_message('Automatic cleanup', extra=extra_meta)

        extra = dict(id=deleted_crash.id, element_created=deleted_crash.created.strftime("%d. %B %Y %I:%M%p"),
                     signature=deleted_crash.signature, userid=deleted_crash.userid, appid=deleted_crash.appid,
                     log_id='36446dc3-ae7c-42ad-ae4e-6a826dcf0a00')
        log_msg = add_extra_to_log_message('Automatic cleanup element', extra=extra)

        mocked_logger = mocked_get_logger.return_value
        with patch('uuid.uuid4') as mocked_uuid4:
            mocked_uuid4.side_effect = (uuid.UUID('36446dc3-ae7c-42ad-ae4e-6a826dcf0a%02d' % x) for x in range(100))
            auto_delete_older_than()

        self.assertEqual(mocked_logger.info.call_count, 11)
        mocked_logger.info.assert_any_call(log_extra_msg)
        mocked_logger.info.assert_any_call(log_msg)

    @patch('logging.getLogger')
    @is_private()
    def test_feedbacks(self, mocked_get_logger):
        gpm['Feedback__limit_storage_days'] = 2
        with freeze_time("2012-12-21 12:00:00"):
            feedbacks = FeedbackFactory.create_batch(10)
        deleted_feedback = feedbacks[-1]
        self.assertEqual(Feedback.objects.all().count(), 10)

        extra_meta = dict(count=10, reason='old', meta=True, log_id='36446dc3-ae7c-42ad-ae4e-6a826dcf0a00',
                          model='Feedback', size='0 bytes')
        log_extra_msg = add_extra_to_log_message('Automatic cleanup', extra=extra_meta)

        extra = dict(id=deleted_feedback.id, element_created=deleted_feedback.created.strftime("%d. %B %Y %I:%M%p"),
                     log_id='36446dc3-ae7c-42ad-ae4e-6a826dcf0a00')
        log_msg = add_extra_to_log_message('Automatic cleanup element', extra=extra)

        mocked_logger = mocked_get_logger.return_value
        with patch('uuid.uuid4') as mocked_uuid4:
            mocked_uuid4.side_effect = (uuid.UUID('36446dc3-ae7c-42ad-ae4e-6a826dcf0a%02d' % x) for x in range(100))
            auto_delete_older_than()

        self.assertEqual(mocked_logger.info.call_count, 11)
        mocked_logger.info.assert_any_call(log_extra_msg)
        mocked_logger.info.assert_any_call(log_msg)


class SizeExceedTest(TestCase):
    @freeze_time("2012-12-21 12:00:00")
    @patch('logging.getLogger')
    @is_private()
    def test_crashes(self, mocked_get_logger):
        gpm['Crash__limit_size'] = 1
        crash_size = 10*1024*1023
        crashes = CrashFactory.create_batch(200, archive_size=crash_size, minidump_size=0)
        deleted_crash = crashes[97]
        self.assertEqual(Crash.objects.all().count(), 200)

        extra_meta = dict(count=98, reason='size_is_exceeded', meta=True, log_id='36446dc3-ae7c-42ad-ae4e-6a826dcf0a00',
                          model='Crash', size='979.0 MB')
        log_extra_msg = add_extra_to_log_message('Automatic cleanup', extra=extra_meta)

        extra = dict(id=deleted_crash.id, element_created=deleted_crash.created.strftime("%d. %B %Y %I:%M%p"),
                     signature=deleted_crash.signature, userid=deleted_crash.userid, appid=deleted_crash.appid,
                     log_id='36446dc3-ae7c-42ad-ae4e-6a826dcf0a00')
        log_msg = add_extra_to_log_message('Automatic cleanup element', extra=extra)

        mocked_logger = mocked_get_logger.return_value
        with patch('uuid.uuid4') as mocked_uuid4:
            mocked_uuid4.side_effect = (uuid.UUID('36446dc3-ae7c-42ad-ae4e-6a826dcf0a%02d' % x) for x in range(100))
            auto_delete_size_is_exceeded()

        self.assertEqual(mocked_logger.info.call_count, 99)
        mocked_logger.info.assert_any_call(log_extra_msg)
        mocked_logger.info.assert_any_call(log_msg)

    @freeze_time("2012-12-21 12:00:00")
    @patch('logging.getLogger')
    @is_private()
    def test_feedbacks(self, mocked_get_logger):
        gpm['Feedback__limit_size'] = 1
        feedback_size = 10*1024*1023
        feedbacks = FeedbackFactory.create_batch(200, screenshot_size=feedback_size, system_logs_size=0, attached_file_size=0,
                                                 blackbox_size=0)
        deleted_feedback = feedbacks[97]
        self.assertEqual(Feedback.objects.all().count(), 200)

        extra_meta = dict(count=98, reason='size_is_exceeded', meta=True, log_id='36446dc3-ae7c-42ad-ae4e-6a826dcf0a00',
                          model='Feedback', size='979.0 MB')
        log_extra_msg = add_extra_to_log_message('Automatic cleanup', extra=extra_meta)

        extra = dict(id=deleted_feedback.id, element_created=deleted_feedback.created.strftime("%d. %B %Y %I:%M%p"),
                     log_id='36446dc3-ae7c-42ad-ae4e-6a826dcf0a00')
        log_msg = add_extra_to_log_message('Automatic cleanup element', extra=extra)

        mocked_logger = mocked_get_logger.return_value
        with patch('uuid.uuid4') as mocked_uuid4:
            mocked_uuid4.side_effect = (uuid.UUID('36446dc3-ae7c-42ad-ae4e-6a826dcf0a%02d' % x) for x in range(100))
            auto_delete_size_is_exceeded()
        self.assertEqual(mocked_logger.info.call_count, 99)
        mocked_logger.info.assert_any_call(log_extra_msg)
        mocked_logger.info.assert_any_call(log_msg)


class ManualCleanupTest(TestCase):
    @freeze_time("2012-12-21 12:00:00")
    @patch('logging.getLogger')
    @is_private()
    def test_crashes(self, mocked_get_logger):
        gpm['Crash__duplicate_number'] = 2
        crashes = CrashFactory.create_batch(10, signature='test')
        deleted_crash = crashes[7]
        self.assertEqual(Crash.objects.count(), 10)

        extra_meta = dict(count=8, reason='manual', meta=True, log_id='36446dc3-ae7c-42ad-ae4e-6a826dcf0a00',
                          model='Crash', limit_duplicated=2, limit_size=None, limit_days=None, size='0 bytes')
        log_extra_msg = add_extra_to_log_message('Manual cleanup', extra=extra_meta)

        extra = dict(id=deleted_crash.id, element_created=deleted_crash.created.strftime("%d. %B %Y %I:%M%p"),
                     signature=deleted_crash.signature, userid=deleted_crash.userid, appid=deleted_crash.appid,
                     log_id='36446dc3-ae7c-42ad-ae4e-6a826dcf0a00')
        log_msg = add_extra_to_log_message('Manual cleanup element', extra=extra)
        mocked_logger = mocked_get_logger.return_value

        with patch('uuid.uuid4') as mocked_uuid4:
            mocked_uuid4.side_effect = (uuid.UUID('36446dc3-ae7c-42ad-ae4e-6a826dcf0a%02d' % x) for x in range(100))
            deferred_manual_cleanup(['crash', 'Crash'], limit_duplicated=2)

        self.assertEqual(mocked_logger.info.call_count, 10)
        mocked_logger.info.assert_any_call(log_extra_msg)
        mocked_logger.info.assert_any_call(log_msg)

    @freeze_time("2012-12-21 12:00:00")
    @patch('logging.getLogger')
    @is_private()
    def test_feedbacks(self, mocked_get_logger):
        gpm['Feedback__limit_size'] = 1
        feedback_size = 100*1024*1023
        feedbacks = FeedbackFactory.create_batch(20, screenshot_size=feedback_size, system_logs_size=0, attached_file_size=0,
                                                 blackbox_size=0)
        deleted_feedback = feedbacks[7]
        self.assertEqual(Feedback.objects.count(), 20)

        extra_meta = dict(count=10, reason='manual', meta=True, log_id='36446dc3-ae7c-42ad-ae4e-6a826dcf0a00',
                          model='Feedback', limit_duplicated=None, limit_size=1, limit_days=None, size='999.0 MB')
        log_extra_msg = add_extra_to_log_message('Manual cleanup', extra=extra_meta)

        extra = dict(id=deleted_feedback.id, element_created=deleted_feedback.created.strftime("%d. %B %Y %I:%M%p"),
                     log_id='36446dc3-ae7c-42ad-ae4e-6a826dcf0a00')
        log_msg = add_extra_to_log_message('Manual cleanup element', extra=extra)
        mocked_logger = mocked_get_logger.return_value

        with patch('uuid.uuid4') as mocked_uuid4:
            mocked_uuid4.side_effect = (uuid.UUID('36446dc3-ae7c-42ad-ae4e-6a826dcf0a%02d' % x) for x in range(100))
            deferred_manual_cleanup(['feedback', 'Feedback'], limit_size=1)
        self.assertEqual(mocked_logger.info.call_count, 11)
        mocked_logger.info.assert_any_call(log_extra_msg)
        mocked_logger.info.assert_any_call(log_msg)

    @freeze_time("2012-12-21 12:00:00")
    @patch('logging.getLogger')
    @is_private()
    def test_symbols(self, mocked_get_logger):
        gpm['Feedback__limit_size'] = 1
        symbols_size = 100*1024*1023
        symbols = SymbolsFactory.create_batch(20, file_size=symbols_size)
        deleted_symbols = symbols[7]
        self.assertEqual(Symbols.objects.count(), 20)

        extra_meta = dict(count=10, reason='manual', meta=True, log_id='36446dc3-ae7c-42ad-ae4e-6a826dcf0a00',
                          model='Symbols', limit_duplicated=None, limit_size=1, limit_days=None, size='999.0 MB')
        log_extra_msg = add_extra_to_log_message('Manual cleanup', extra=extra_meta)

        extra = dict(id=deleted_symbols.id, element_created=deleted_symbols.created.strftime("%d. %B %Y %I:%M%p"),
                     log_id='36446dc3-ae7c-42ad-ae4e-6a826dcf0a00')
        log_msg = add_extra_to_log_message('Manual cleanup element', extra=extra)
        mocked_logger = mocked_get_logger.return_value

        with patch('uuid.uuid4') as mocked_uuid4:
            mocked_uuid4.side_effect = (uuid.UUID('36446dc3-ae7c-42ad-ae4e-6a826dcf0a%02d' % x) for x in range(100))
            deferred_manual_cleanup(['crash', 'Symbols'], limit_size=1)
        self.assertEqual(mocked_logger.info.call_count, 11)
        mocked_logger.info.assert_any_call(log_extra_msg)
        mocked_logger.info.assert_any_call(log_msg)

    @freeze_time("2012-12-21 12:00:00")
    @patch('logging.getLogger')
    @is_private()
    def test_omaha_versions(self, mocked_get_logger):
        gpm['Version__limit_size'] = 1
        version_size = 1000*1024*1023
        versions = VersionFactory.create_batch(2, file_size=version_size)
        deleted_version = versions[0]
        self.assertEqual(Version.objects.count(), 2)

        extra_meta = dict(count=1, reason='manual', meta=True, log_id='36446dc3-ae7c-42ad-ae4e-6a826dcf0a00',
                          model='Version', limit_duplicated=None, limit_size=1, limit_days=None, size='999.0 MB')
        log_extra_msg = add_extra_to_log_message('Manual cleanup', extra=extra_meta)

        extra = dict(id=deleted_version.id, element_created=deleted_version.created.strftime("%d. %B %Y %I:%M%p"),
                     log_id='36446dc3-ae7c-42ad-ae4e-6a826dcf0a00')
        log_msg = add_extra_to_log_message('Manual cleanup element', extra=extra)
        mocked_logger = mocked_get_logger.return_value

        with patch('uuid.uuid4') as mocked_uuid4:
            mocked_uuid4.side_effect = (uuid.UUID('36446dc3-ae7c-42ad-ae4e-6a826dcf0a%02d' % x) for x in range(100))
            deferred_manual_cleanup(['omaha', 'Version'], limit_size=1)
        self.assertEqual(mocked_logger.info.call_count, 2)
        mocked_logger.info.assert_any_call(log_extra_msg)
        mocked_logger.info.assert_any_call(log_msg)

    @freeze_time("2012-12-21 12:00:00")
    @patch('logging.getLogger')
    @is_private()
    def test_sparkle_versions(self, mocked_get_logger):
        gpm['SparkleVersion__limit_size'] = 1
        version_size = 1000*1024*1023
        versions = SparkleVersionFactory.create_batch(2, file_size=version_size)
        deleted_version = versions[0]
        self.assertEqual(SparkleVersion.objects.count(), 2)

        extra_meta = dict(count=1, reason='manual', meta=True, log_id='36446dc3-ae7c-42ad-ae4e-6a826dcf0a00',
                          model='SparkleVersion', limit_duplicated=None, limit_size=1, limit_days=None, size='999.0 MB')
        log_extra_msg = add_extra_to_log_message('Manual cleanup', extra=extra_meta)

        extra = dict(id=deleted_version.id, element_created=deleted_version.created.strftime("%d. %B %Y %I:%M%p"),
                     log_id='36446dc3-ae7c-42ad-ae4e-6a826dcf0a00')
        log_msg = add_extra_to_log_message('Manual cleanup element', extra=extra)
        mocked_logger = mocked_get_logger.return_value

        with patch('uuid.uuid4') as mocked_uuid4:
            mocked_uuid4.side_effect = (uuid.UUID('36446dc3-ae7c-42ad-ae4e-6a826dcf0a%02d' % x) for x in range(100))
            deferred_manual_cleanup(['sparkle', 'SparkleVersion'], limit_size=1)
        self.assertEqual(mocked_logger.info.call_count, 2)
        mocked_logger.info.assert_any_call(log_extra_msg)
        mocked_logger.info.assert_any_call(log_msg)
