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

from uuid import UUID
from django.core.files.uploadedfile import SimpleUploadedFile

import factory


class ApplicationFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'omaha.Application'

    id = factory.Sequence(lambda n: '{D0AB2EBC-931B-4013-9FEB-C9C4C2225%s}' % n)
    name = factory.Sequence(lambda n: 'chrome%s' % n)


class DataFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'omaha.Data'

    app = factory.lazy_attribute(lambda x: ApplicationFactory())
    name = 0
    index = factory.Sequence(lambda n: 'indext_test%s' % n)
    value = factory.Sequence(lambda n: 'test%s' % n)


class PlatformFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'omaha.Platform'

    name = factory.Sequence(lambda n: 'p_%s' % n)


class ChannelFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'omaha.Channel'

    name = factory.Sequence(lambda n: 'channel%s' % n)


class VersionFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'omaha.Version'

    app = factory.lazy_attribute(lambda x: ApplicationFactory())
    platform = factory.lazy_attribute(lambda x: PlatformFactory())
    channel = factory.lazy_attribute(lambda x: ChannelFactory())
    version = '37.0.2062.124'
    file = SimpleUploadedFile('./chrome_installer.exe', b' ' * 123)
    file_size = 123
    file_hash = 'ojan8ermbNHlI5czkED+nc01rxk='


class RequestFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'omaha.Request'

    version = "1.0.0.0"
    userid = UUID(int=0)


class AppRequestFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'omaha.AppRequest'

    request = factory.LazyAttribute(lambda x: RequestFactory())
    appid = '{D0AB2EBC-931B-4013-9FEB-C9C4C2225C0}'

    @factory.post_generation
    def events(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for event in extracted:
                self.events.add(event)


class ActionFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'omaha.Action'

    version = factory.lazy_attribute(lambda x: VersionFactory())
    event = 1


class EventFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'omaha.Event'

    eventtype = 1
    eventresult = 1
