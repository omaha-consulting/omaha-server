# coding: utf8

from django.test import TestCase
from ..models import DummyModel, DummyModelCustomBit


class VersionFieldTest(TestCase):
    def setUp(self):
        DummyModel.objects.create(version="0.1")
        DummyModel.objects.create(version="1.0")
        DummyModel.objects.create(version="1.0.1")

    def test_get_by_exact_version(self):
        thing = DummyModel.objects.get(version="0.1")
        self.assertEqual(thing.version, "0.1")
        self.assertEqual(thing.version, "0.1.0")

    def test_filter_by_greater_than_version(self):
        things = DummyModel.objects.filter(version__gt="0.1")
        self.assertEqual(len(things), 2)

        things = DummyModel.objects.filter(version__gt="1.0")
        self.assertEqual(len(things), 1)

        things = DummyModel.objects.filter(version__gt="1.0.1")
        self.assertEqual(len(things), 0)

    def test_filter_by_less_than_version(self):
        things = DummyModel.objects.filter(version__lt="0.1")
        self.assertEqual(len(things), 0)

        things = DummyModel.objects.filter(version__lt="1.0")
        self.assertEqual(len(things), 1)

        things = DummyModel.objects.filter(version__lt="1.0.1")
        self.assertEqual(len(things), 2)

    def test_overflow_number(self):
        error_occured = False
        try:
            overflow = DummyModel.objects.create(version="1.999.1")
        except ValueError:
            error_occured = True
        self.assertTrue(error_occured)


class VersionFieldCustomBitsTest(TestCase):
    def setUp(self):
        DummyModelCustomBit.objects.create(version="1.999.1")

    def test_get_by_exact_version(self):
        thing = DummyModelCustomBit.objects.get(version="1.999.1")
        self.assertEqual(thing.version, "1.999.1")
