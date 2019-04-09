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

import os
from datetime import datetime
from unittest import TestCase

from lxml import etree
from xmlunittest import XmlTestMixin

from omaha.tests import fixtures

from omaha.utils import get_sec_since_midnight
from omaha.core import (
    Url,
    Urls,
    Package,
    Packages,
    Action,
    Actions,
    Manifest,
    Updatecheck,
    Updatecheck_negative,
    Updatecheck_positive,
    App,
    Response,
    Ping,
    Event,
    Data,
)


BASE_DIR = os.path.dirname(__file__)
RESPONSE_XSD_FILE = os.path.join(BASE_DIR, '..', 'response.xsd')


class TestRequestScheme(TestCase, XmlTestMixin):
    url = 'http://cache.pack.google.com/edgedl/chrome/install/782.112/'

    package_attr = dict(
        name='chrome_installer.exe',
        required='true',
        size='23963192',
        hash='VXriGUVI0TNqfLlU02vBel4Q3Zo=',
        fp='fp',
    )

    action_attr = dict(
        event='install',
        arguments='--do-not-launch-chrome',
        run='chrome_installer.exe',
    )

    manifest_attr = dict(
        version='13.0.782.112',
    )

    app_attr = dict(
        app_id='{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}',
    )

    def test_ping(self):
        root = Ping()
        self.assertXmlNode(root, tag='ping', text=None)
        self.assertXmlHasAttribute(root, 'status', expected_value='ok')

    def test_event(self):
        root = Event()
        self.assertXmlNode(root, tag='event', text=None)
        self.assertXmlHasAttribute(root, 'status', expected_value='ok')

    def test_data(self):
        root = Data('install', index='verboselogging', text='app-specific values here')
        self.assertXmlNode(root, tag='data', text='app-specific values here')
        self.assertXmlHasAttribute(root, 'status', expected_value='ok')
        self.assertXmlHasAttribute(root, 'index', expected_value='verboselogging')

        root = Data('untrusted')
        self.assertXmlNode(root, tag='data', text=None)
        self.assertXmlHasAttribute(root, 'status', expected_value='ok')

    def test_url(self):
        root = Url(self.url)

        self.assertXmlNode(root, tag='url', text=None)
        self.assertXmlHasAttribute(root, 'codebase', expected_value=self.url)

    def test_urls(self):
        root = Urls([self.url] * 3)

        self.assertXmlNode(root, tag='urls', text=None)
        self.assertXpathsExist(root, ('./url', './url[@codebase="%s"]' % self.url))

    def test_package(self):
        root = Package(**self.package_attr)

        self.assertXmlNode(root, tag='package', text=None)

        for key, val in list(self.package_attr.items()):
            self.assertXmlHasAttribute(root, key, expected_value=val)

    def test_packages(self):
        root = Packages([Package(**self.package_attr)] * 5)

        self.assertXmlNode(root, tag='packages', text=None)
        self.assertXpathsExist(root, ('./package',))

        for key, val in list(self.package_attr.items()):
            self.assertXpathsExist(root, ('./package[@{0}="{1}"]'.format(key, val),))

    def test_action(self):
        root = Action(**self.action_attr)

        self.assertXmlNode(root, tag='action', text=None)

        for key, val in list(self.action_attr.items()):
            self.assertXmlHasAttribute(root, key, expected_value=val)

    def test_actions(self):
        root = Actions([Action(**self.action_attr)])

        self.assertXmlNode(root, tag='actions', text=None)
        self.assertXpathsExist(root, ('./action',))

        for key, val in list(self.action_attr.items()):
            self.assertXpathsExist(root, ('./action[@{0}="{1}"]'.format(key, val),))

    def test_manifest(self):
        root = Manifest(packages=Packages([Package(**self.package_attr)] * 5),
                        actions=Actions([Action(**self.action_attr)] * 5),
                        **self.manifest_attr)

        self.assertXmlNode(root, tag='manifest', text=None)
        self.assertXmlHasAttribute(root, 'version', expected_value=self.manifest_attr['version'])
        self.assertXpathsExist(root, ('./packages',))
        self.assertXpathsExist(root, ('./actions',))

        for key, val in list(self.action_attr.items()):
            self.assertXpathsExist(root, ('./actions/action[@{0}="{1}"]'.format(key, val),))

        for key, val in list(self.package_attr.items()):
            self.assertXpathsExist(root, ('./packages/package[@{0}="{1}"]'.format(key, val),))

    def test_updatecheck(self):
        root = Updatecheck()

        self.assertXmlNode(root, tag='updatecheck', text=None)
        self.assertXmlHasAttribute(root, 'status', expected_value='noupdate')

    def test_updatecheck_negative(self):
        root = Updatecheck_negative()

        self.assertXmlNode(root, tag='updatecheck', text=None)
        self.assertXmlHasAttribute(root, 'status', expected_value='noupdate')

    def test_updatecheck_positive(self):
        root = Updatecheck_positive(
            urls=[self.url] * 5,
            manifest=Manifest(packages=Packages([Package(**self.package_attr)] * 5),
                              actions=Actions([Action(**self.action_attr)] * 5),
                              **self.manifest_attr)
        )

        self.assertXmlNode(root, tag='updatecheck', text=None)
        self.assertXmlHasAttribute(root, 'status', expected_value='ok')
        self.assertXpathsExist(root, ('./urls',))
        self.assertXpathsExist(root, ('./manifest',))

        for key, val in list(self.action_attr.items()):
            self.assertXpathsExist(root, ('./manifest/actions/action[@{0}="{1}"]'.format(key, val),))

        for key, val in list(self.package_attr.items()):
            self.assertXpathsExist(root, ('./manifest/packages/package[@{0}="{1}"]'.format(key, val),))

    def test_app(self):
        root = App(
            updatecheck=Updatecheck_negative(),
            **self.app_attr)

        self.assertXmlNode(root, tag='app', text=None)
        self.assertXmlHasAttribute(root, 'status', expected_value='ok')
        self.assertXmlHasAttribute(root, 'appid', expected_value=self.app_attr['app_id'])
        self.assertXpathsExist(root, ('./updatecheck',))

    def test_response(self):
        now = datetime.utcnow()
        elapsed_seconds = get_sec_since_midnight(now)
        root = Response(
            date=now,
            apps_list=[App(updatecheck=Updatecheck_negative(), **self.app_attr)])

        self.assertXmlNode(root, tag='response', text=None)
        self.assertXpathsExist(root, ('./daystart',))
        self.assertXpathsExist(root, ('./app',))
        self.assertXpathsExist(root, ('./daystart[@elapsed_seconds="%s"]' % elapsed_seconds,))

    def test_valid_response_negative(self):
        response = Response(
            server='prod',
            protocol='3.0',
            date=datetime(2014, 1, 1, hour=15, minute=41, second=48),  # 56508 sec
            apps_list=[
                App('{430FD4D0-B729-4F61-AA34-91526481799D}', updatecheck=Updatecheck_negative(), ping=True),
                App('{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}', updatecheck=Updatecheck_negative(), ping=True),
            ]
        )

        self.assertXmlValidXSchema(response, filename=RESPONSE_XSD_FILE)
        self.assertXmlEquivalentOutputs(etree.tostring(response), fixtures.response_update_check_negative)

    def test_valid_response_positive(self):
        updatecheck = Updatecheck_positive(
            urls=['http://cache.pack.google.com/edgedl/chrome/install/782.112/'],
            manifest=Manifest(
                version='13.0.782.112',
                packages=Packages([Package(
                    name='chrome_installer.exe',
                    required='true',
                    size='23963192',
                    hash='VXriGUVI0TNqfLlU02vBel4Q3Zo=',
                )]),
                actions=Actions([
                    Action(event='install', arguments='--do-not-launch-chrome', run='chrome_installer.exe'),
                    Action(event='postinstall', version='13.0.782.112', onsuccess='exitsilentlyonlaunchcmd'),
                ])
            )
        )
        app = App(
            '{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}',
            status='ok',
            updatecheck=updatecheck,
            ping=True,
        )

        response = Response(
            server='prod',
            protocol='3.0',
            date=datetime(2014, 1, 1, hour=15, minute=41, second=48),  # 56508 sec
            apps_list=[
                App('{430FD4D0-B729-4F61-AA34-91526481799D}', status='ok',
                    ping=True, updatecheck=Updatecheck_negative()),
                app,
            ]
        )

        self.assertXmlValidXSchema(response, filename=RESPONSE_XSD_FILE)
        self.assertXmlEquivalentOutputs(etree.tostring(response), fixtures.response_update_check_positive)

    def test_valid_response_event(self):
        response = Response(
            date=datetime(year=2014, month=1, day=1, hour=15, minute=45, second=54),
            apps_list=[App(
                app_id='{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}',
                status='ok',
                events=[Event(), Event(), Event()]
            )]
        )

        self.assertXmlValidXSchema(response, filename=RESPONSE_XSD_FILE)
        self.assertXmlEquivalentOutputs(etree.tostring(response), fixtures.response_event)

    def test_valid_response_data(self):
        response = Response(
            date=datetime(year=2014, month=1, day=1, hour=15, minute=45, second=54),
            apps_list=[App(
                app_id='{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}',
                status='ok',
                data_list=[
                    Data('install', index='verboselogging', text='app-specific values here'),
                    Data('untrusted')
                ]
            )]
        )

        self.assertXmlValidXSchema(response, filename=RESPONSE_XSD_FILE)
        self.assertXmlEquivalentOutputs(etree.tostring(response), fixtures.response_data_doc)
