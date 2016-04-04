# coding: utf8

import datetime

from django.test import TestCase
from django.core.management import call_command
from django.core.files.uploadedfile import SimpleUploadedFile

from bitmapist import YearEvents

from omaha.tests.utils import temporary_media_root
from omaha.utils import redis
from omaha.models import (
    Application,
    Platform,
    Channel,
    Version,
    Request,
    AppRequest
)


class GenerateFakeDataTest(TestCase):
    @temporary_media_root()
    def setUp(self):
        redis.flushdb()
        self.app = Application.objects.create(id='{5FAD27D4-6BFA-4daa-A1B3-5A1F821FEE0F}', name='app')
        self.channel = Channel.objects.create(name='stable')
        self.platform = Platform.objects.create(name='win')
        self.version1 = Version.objects.create(
            app=self.app,
            platform=self.platform,
            channel=self.channel,
            version='1.0.0.0',
            file=SimpleUploadedFile('./chrome_installer.exe', False))
        self.version2 = Version.objects.create(
            app=self.app,
            platform=self.platform,
            channel=self.channel,
            version='2.0.0.0',
            file=SimpleUploadedFile('./chrome_installer.exe', False))

    def tearDown(self):
        redis.flushdb()

    def test_command(self):
        self.assertEqual(0, Request.objects.all().count())
        call_command('generate_fake_data', self.app.id, count=10)
        self.assertEqual(10, Request.objects.all().count())
        self.assertEqual(10, AppRequest.objects.filter(appid=self.app.id).count())


class GenerateFakeStatisticsTest(TestCase):
    @temporary_media_root()
    def setUp(self):
        redis.flushdb()
        self.app = Application.objects.create(id='{5FAD27D4-6BFA-4daa-A1B3-5A1F821FEE0F}', name='app')
        self.channel = Channel.objects.create(name='stable')
        self.platform = Platform.objects.create(name='win')
        self.version1 = Version.objects.create(
            app=self.app,
            platform=self.platform,
            channel=self.channel,
            version='1.0.0.0',
            file=SimpleUploadedFile('./chrome_installer.exe', False))
        self.version2 = Version.objects.create(
            app=self.app,
            platform=self.platform,
            channel=self.channel,
            version='2.0.0.0',
            file=SimpleUploadedFile('./chrome_installer.exe', False))

    def tearDown(self):
        redis.flushdb()

    def test_command(self):
        now = datetime.datetime.now()
        year = now.year
        self.assertEqual(0, len(YearEvents('request', year)))
        call_command('generate_fake_statistics', self.app.id, count=10)
        self.assertEqual(10, len(YearEvents('request', year)))
