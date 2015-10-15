
import os
from lxml import objectify
import logging

from django.test import LiveServerTestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.db import connections

import requests

from crash.models import Crash
from sparkle.factories import SparkleVersionFactory
from omaha.factories import ChannelFactory, ApplicationFactory


@override_settings(
    CELERY_ALWAYS_EAGER=False,
    CELERY_EAGER_PROPAGATES_EXCEPTIONS=False,
)
class PublicTests(LiveServerTestCase):

    def setUp(self):
        if settings.IS_PRIVATE:
            self.skipTest('Live server should be public')
        connections['default'].settings_dict['USER'] = os.environ.get('DB_PUBLIC_USER')
        connections['default'].settings_dict['PASSWORD'] = os.environ.get('DB_PUBLIC_PASSWORD')
        connections['default'].close()
        url = '%s/%s' % (self.live_server_url, 'admin/')
        resp = requests.get(url)
        self.assertEqual(resp.status_code, 404)

    def tearDown(self):
        from django.db import connections
        import os
        connections['default'].settings_dict['USER'] = os.environ.get('DB_USER', 'postgres')
        connections['default'].settings_dict['PASSWORD'] = os.environ.get('DB_PASSWORD', '')
        connections['default'].close()

    def test_public_crash_upload(self):
        url = '%s%s' % (self.live_server_url, '/service/crash_report/')
        mini_dump_file = SimpleUploadedFile("minidump.dat", b"content")
        form_data = dict(
            appid='{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}',
            userid='{2882CF9B-D9C2-4edb-9AAF-8ED5FCF366F7}',
        )
        files = dict(
            upload_file_minidump=mini_dump_file,
        )
        self.assertEqual(Crash.objects.all().count(), 0)
        response = requests.post(url, form_data, files=files)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Crash.objects.all().count(), 1)
        obj = Crash.objects.get()
        self.assertEqual(response.content.decode(), str(obj.pk))
        self.assertIsNotNone(obj.upload_file_minidump)

    def test_public_sparkle_update(self):
        # import pdb; pdb.set_trace()
        ChannelFactory._meta.database = 'root'
        channel = ChannelFactory(name='test')
        app_name = 'SparrowTestApp'
        ApplicationFactory._meta.database='root'
        app = ApplicationFactory(name=app_name)
        file = SimpleUploadedFile("test.dmg", b"content")
        SparkleVersionFactory._meta.database='root'
        s = SparkleVersionFactory.create(channel=channel, app=app, file=file)
        # import pdb; pdb.set_trace()
        url = '%s%s' % (self.live_server_url, '/sparkle/SparrowTestApp/test/appcast.xml')
        resp = requests.get(url)
        # logging.error(resp.content)
        root = objectify.fromstring(resp.content)
        self.assertTrue(app_name in str(root.channel.item.title))

    def test_public_omaha_update(self):
        url = '%s%s' % (self.live_server_url, '/service/update2')
        body = '<?xml version="1.0" encoding="UTF-8"?> <request installsource="scheduler" ismachine="0" protocol="3.0" requestid="{F77BCC0B-BB7C-4396-8071-01063EB72E4F}" sessionid="{81586D86-30A4-44CA-B396-0D8AC0113836}" testsource="auto" version="1.3.25.0"> <os arch="x64" platform="win" sp="Service Pack 1" version="6.1"/> <app appid="{8A76FC95-0086-4BCE-9517-DC09DDB5652F}" brand="GGLS" client="" installage="4" lang="en" nextversion="" version="36.0.2060.0"> <updatecheck/> </app> <app appid="{F07B3878-CD6F-4B96-B52F-95C4D23077E0}" brand="" client="" installage="6" lang="en" nextversion="13.0.782.112" version=""> <event errorcode="0" eventresult="1" eventtype="9" extracode1="0"/> <event errorcode="0" eventresult="1" eventtype="5" extracode1="0"/> <event errorcode="-2147219440" eventresult="4" eventtype="2" extracode1="268435463"/> </app> </request>'
        headers = {'Content-Type': 'application/xml'}
        requests.post(url, data=body, headers=headers)