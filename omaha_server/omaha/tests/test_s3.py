import os
from django.test import TestCase, override_settings

import moto
import boto
import mock
import omaha
from boto.s3.key import Key

from crash.factories import CrashFactoryWithFiles, SymbolsFactory
from feedback.factories import FeedbackFactory
from omaha.factories import VersionFactory
from sparkle.factories import SparkleVersionFactory

from crash.models import Crash, Symbols
from feedback.models import Feedback
from omaha.models import Version
from omaha.tests import OverloadTestStorageMixin
from sparkle.models import SparkleVersion
from omaha_server.utils import storage_with_spaces_instance
from omaha.limitation import bulk_delete
from storages.backends.s3boto import S3BotoStorage
from omaha.tasks import get_prefix


class BaseS3Test(object):
    model = None
    factory = None
    file_fields = None
    files = None

    @moto.mock_s3_deprecated
    def test_model_delete(self):
        conn = boto.connect_s3()
        conn.create_bucket('test')
        obj = self.factory()

        keys = conn.get_bucket('test').get_all_keys()
        keys = [key.name for key in keys]
        for field in self.file_fields:
            self.assertIn(getattr(obj, field).name, keys)

        obj.delete()
        keys = conn.get_bucket('test').get_all_keys()
        self.assertFalse(keys)

    @moto.mock_s3_deprecated
    def test_model_update(self):
        conn = boto.connect_s3()
        conn.create_bucket('test')
        obj = self.factory()
        new_obj = self.factory()

        old_keys = conn.get_bucket('test').get_all_keys()
        old_keys = [key.name for key in old_keys]

        for field in self.file_fields:
            self.assertIn(getattr(obj, field).name, old_keys)
            setattr(obj, field, getattr(new_obj, field))
            obj.save()

        new_keys = conn.get_bucket('test').get_all_keys()
        self.assertFalse(set(old_keys) & set(new_keys))

    @moto.mock_s3_deprecated
    def test_bulk_delete(self):
        conn = boto.connect_s3()
        conn.create_bucket('test')
        self.factory.create_batch(10)
        qs = self.model.objects.all()
        self.assertEqual(qs.count(), 10)
        keys = conn.get_bucket('test').get_all_keys()
        self.assertEqual(len(keys), len(self.file_fields) * 10)
        with mock.patch('boto.__init__') as my_mock:
            my_mock.connect_s3.return_value = conn
            try:                                    # When we try to delete nonexistent key from s3 in pre_delete signal
                bulk_delete(self.model, qs)         # original boto doesn't raise S3ResponseError: 404 Not Found
            except boto.exception.S3ResponseError:  # but mocked boto does
                pass

        keys = conn.get_bucket('test').get_all_keys()
        self.assertFalse(keys)

    @moto.mock_s3_deprecated
    def test_dangling_delete_db(self):
        conn = boto.connect_s3()
        conn.create_bucket('test')
        bucket = conn.get_bucket('test')
        self.factory.create_batch(2)
        keys = [key.name for key in conn.get_bucket('test').get_all_keys()]
        bucket.delete_key(keys[0])
        result = omaha.limitation.handle_dangling_files(
            self.model,
            get_prefix(self.model),
            self.file_fields
        )
        self.assertEqual(result['status'], 'Send notifications')

    @moto.mock_s3_deprecated
    def test_dangling_delete_s3(self):
        # create bucket and send file in s3
        conn = boto.connect_s3()
        conn.create_bucket('test')
        bucket = conn.get_bucket('test')
        prefix = get_prefix(self.model)
        for f in self.files:
            k = Key(bucket, '%s/%s' % (f['prefix'], f['file_path']))
            with open(f['file_path'], 'rb') as test_file:
                k.send_file(test_file)
        # create 2 files in db
        self.factory.create_batch(2)
        result = omaha.limitation.handle_dangling_files(
            self.model,
            prefix,
            self.file_fields
        )
        for _file in result['data']:
            self.assertFalse(
                _file in [key.name for key in conn.get_bucket('test').get_all_keys()]
            )


@override_settings(DEFAULT_FILE_STORAGE='storages.backends.s3boto.S3BotoStorage')
class CrashS3Test(BaseS3Test, TestCase):
    model = Crash
    factory = CrashFactoryWithFiles
    file_fields = ['archive', 'upload_file_minidump']
    files = ({
        'prefix': 'minidump_archive',
        'file_path': os.path.abspath(
            'crash/tests/testdata/7b05e196-7e23-416b-bd13-99287924e214.dmp'
        )
    },)


@override_settings(DEFAULT_FILE_STORAGE='storages.backends.s3boto.S3BotoStorage')
class FeedbackS3Test(BaseS3Test, TestCase):
    model = Feedback
    factory = FeedbackFactory
    file_fields = ['screenshot', 'blackbox', 'system_logs', 'attached_file']
    files = ({
        'prefix': 'screenshot',
        'file_path': os.path.abspath('feedback/tests/testdata/test_png.png')
    },)


@override_settings(DEFAULT_FILE_STORAGE='storages.backends.s3boto.S3BotoStorage')
class SymbolsS3Test(BaseS3Test, TestCase):
    model = Symbols
    factory = SymbolsFactory
    file_fields = ['file']
    files = ({
        'prefix': 'symbols',
        'file_path': os.path.abspath(
            'crash/tests/testdata/symbols/BreakpadTestApp.pdb/C1C0FA629EAA4B4D9DD2ADE270A231CC1/BreakpadTestApp.sym'
        )
    },)

    def setUp(self):
        storage_with_spaces_instance._setup()


@override_settings(DEFAULT_FILE_STORAGE='storages.backends.s3boto.S3BotoStorage')
class OmahaVersionS3Test(OverloadTestStorageMixin, BaseS3Test, TestCase):
    model = Version
    factory = VersionFactory
    file_fields = ['file']
    files = ({
        'prefix': 'build',
        'file_path': os.path.abspath('feedback/tests/testdata/test_png.png')
    },)


@override_settings(DEFAULT_FILE_STORAGE='storages.backends.s3boto.S3BotoStorage')
class SparkleVersionS3Test(OverloadTestStorageMixin, BaseS3Test, TestCase):
    model = SparkleVersion
    factory = SparkleVersionFactory
    file_fields = ['file']
    files = ({
        'prefix': 'sparkle',
        'file_path': os.path.abspath('feedback/tests/testdata/test_png.png')
    },)
