# coding: utf8
import os

from django import test
from feedback.utils import get_file_extension

BASE_DIR = os.path.dirname(__file__)
TEST_DATA_DIR = os.path.join(BASE_DIR, 'testdata')
GZ_FILE = os.path.join(TEST_DATA_DIR, 'test_tar_gz')
TAR_FILE = os.path.join(TEST_DATA_DIR, 'test_tar')
TEXT_FILE = os.path.join(TEST_DATA_DIR, 'test_none')


class UtilsTest(test.TestCase):

    def test_get_file_extension_from_gz_file(self):
        with open(GZ_FILE, 'rb') as file:
            file_header = file.read(1024)
        file_description = get_file_extension(file_header)
        self.assertEqual(file_description['file_extension'], "tar.gz")
        self.assertIn(file_description['mime_type'],
                      ["application/x-gzip", "application/gzip"])

    def test_get_file_extension_from_tar_file(self):
        with open(TAR_FILE, 'rb') as file:
            file_header = file.read(1024)
        file_description = get_file_extension(file_header)
        self.assertEqual(file_description['file_extension'], "tar")
        self.assertEqual(file_description['mime_type'], "application/x-tar")

    def test_get_file_extension_from_none_extension_file(self):
        with open(TEXT_FILE, 'rb') as file:
            file_header = file.read(1024)
        file_description = get_file_extension(file_header)
        self.assertEqual(file_description['file_extension'], None)
        self.assertEqual(file_description['mime_type'], "text/plain")
