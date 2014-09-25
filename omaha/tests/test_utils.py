# coding: utf8

from datetime import datetime
from unittest import TestCase

from omaha.utils import get_sec_since_midnight


class UtilsTest(TestCase):
    def test_get_seconds_since_midnight(self):
        self.assertEqual(43,
                         get_sec_since_midnight(datetime(year=2014,
                                                         month=1,
                                                         day=1,
                                                         second=43)))

        self.assertEqual(0,
                         get_sec_since_midnight(datetime(year=2014,
                                                         month=1,
                                                         day=1)))

        self.assertEqual(3600,
                         get_sec_since_midnight(datetime(year=2014,
                                                         month=1,
                                                         day=1,
                                                         hour=1)))

        self.assertEqual((16 * 3600) + (23 * 60) + 17,
                         get_sec_since_midnight(datetime(year=2014,
                                                         month=1,
                                                         day=1,
                                                         hour=16,
                                                         minute=23,
                                                         second=17)))
