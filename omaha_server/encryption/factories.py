# coding: utf8

"""
This software is licensed under the Apache 2 license, quoted below.

Copyright 2015 Crystalnix Limited

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


import factory

class GeneratedKeyFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'encryption.GeneratedKey'

    type = 'db'
    is_enabled = True
    private_key = factory.Sequence(lambda n: 'Private key #%s' % n)
    public_key = factory.Sequence(lambda n: 'Public key #%s' % n)

class DecryptionDataFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'encryption.DecryptionData'

    key = factory.lazy_attribute(lambda x: GeneratedKeyFactory())
    encrypted_aes_key = 'c29tZV9rZXk='