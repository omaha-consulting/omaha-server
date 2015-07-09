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

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class PercentField(models.FloatField):
    """
    Float field that ensures field value is in the range 0-100.
    """
    def formfield(self, **kwargs):
        defaults = {'min_value': 0, 'max_value': 100}
        defaults.update(kwargs)
        return super(PercentField, self).formfield(**defaults)

    default_validators = [
        MinValueValidator(0),
        MaxValueValidator(100),
    ]
