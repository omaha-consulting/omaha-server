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

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import signals

import factory


class SymbolsFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'crash.Symbols'

    file = SimpleUploadedFile('./fake.sym', b' ' * 123)
    debug_id = factory.Sequence(lambda n: 'C1C0FA629EAA4B4D9DD2ADE270A231C%s' % n)
    debug_file = factory.Sequence(lambda n: 'BreakpadTestApp_%s.pdb' % n)


class CrashFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'crash.Crash'

    appid = factory.Sequence(lambda n: '{D0AB2EBC-931B-4013-9FEB-C9C4C2225%s}' % n)
    userid = factory.Sequence(lambda n: '{D0AB2EBC-931B-4013-9FEB-C9C4C2225%s}' % n)
    meta = {'lang': 'en'}
    signature = factory.Sequence(lambda n: 'signature_%s' % n)


@factory.django.mute_signals(signals.post_save)
class CrashFactoryWithFiles(CrashFactory):

    archive = factory.django.FileField(filename='the_file.dat')
    upload_file_minidump = factory.django.FileField(filename='the_file.dat')


class CrashDescriptionFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'crash.CrashDescription'

    crash = factory.lazy_attribute(lambda x: CrashFactory())
    summary = 'Test Summary'
    description = 'Test Description'
