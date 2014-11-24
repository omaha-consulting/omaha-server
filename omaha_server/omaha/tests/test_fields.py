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

from django.test import TestCase
from django.utils.functional import lazy

from omaha.fields import PercentField


class PercentFieldTest(TestCase):
    def test_PercentField(self):
        lazy_func = lazy(lambda: 1.2, float)
        self.assertIsInstance(PercentField().get_prep_value(lazy_func()), float)
        self.assertEqual(PercentField.default_validators[0].limit_value, 0)
        self.assertEqual(PercentField.default_validators[1].limit_value, 100)
