# coding: utf8

import factory


class ApplicationFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'omaha.Application'

    id = '{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}'
    name = 'chrome2'


class PlatformFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'omaha.Platform'

    name = 'win'


class ChannelFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'omaha.Channel'

    name = 'release'


class VersionFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'omaha.Version'

    app = factory.lazy_attribute(lambda x: ApplicationFactory())
    platform = factory.lazy_attribute(lambda x: PlatformFactory())
    channel = factory.lazy_attribute(lambda x: ChannelFactory())
    version = '37.0.2062.124'
    file = factory.django.FileField(filename='./chrome_installer.exe')
    file_hash = 'VXriGUVI0TNqfLlU02vBel4Q3Zo='
