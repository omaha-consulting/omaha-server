# coding: utf8

from django.test import TestCase
from django.test import override_settings
from mock import Mock

from omaha_server.utils import show_toolbar


class UtilsTest(TestCase):
    def setUp(self):
        self.request = Mock()

    def test_show_toolbar_ajax(self):
        self.request.is_ajax = lambda: True
        self.assertFalse(show_toolbar(self.request))

    @override_settings(DEBUG=True)
    def test_show_toolbar_debug_true(self):
        self.request.is_ajax = lambda: False
        self.assertTrue(show_toolbar(self.request))

    @override_settings(DEBUG=False)
    def test_show_toolbar_debug_false(self):
        self.request.is_ajax = lambda: False
        self.assertFalse(show_toolbar(self.request))
