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

import pytz
from datetime import datetime

from django.forms import IntegerField
from django.core.validators import MinValueValidator

from dynamic_preferences.types import IntegerPreference, ChoicePreference
from dynamic_preferences import global_preferences_registry
from django_select2.forms import Select2Widget

class PositiveIntegerField(IntegerField):
    min_value = 1
    default_validators = [MinValueValidator(min_value)]

    def __init__(self, *args, **kwargs):
        defaults = {'min_value': self.min_value}
        defaults.update(kwargs)
        super(PositiveIntegerField, self).__init__(**defaults)


class PositiveIntegerPreference(IntegerPreference):
    field_class = PositiveIntegerField

@global_preferences_registry.register
class CrashLimitStorageDays(PositiveIntegerPreference):
    section = 'Crash'
    verbose_name = 'Maximum storage time (days) for crashes'
    name = "limit_storage_days"
    default = 360


@global_preferences_registry.register
class CrashLimitStorageSize(PositiveIntegerPreference):
    section = 'Crash'
    verbose_name = "Maximum crash storage utilization (GB)"
    name = "limit_size"
    default = 100


@global_preferences_registry.register
class CrashLimitDuplicateNumber(PositiveIntegerPreference):
    section = 'Crash'
    verbose_name = 'Maximum number duplicate crashes'
    name = "duplicate_number"
    default = 10


@global_preferences_registry.register
class OmahaLimitSize(PositiveIntegerPreference):
    section = 'Version'
    verbose_name = "Alert when Omaha version storage exceeds (GB) "
    name = "limit_size"
    default = 100


@global_preferences_registry.register
class SparkleLimitSize(PositiveIntegerPreference):
    section = 'SparkleVersion'
    verbose_name = "Alert when Sparkle version storage exceeds (GB) "
    name = "limit_size"
    default = 100


@global_preferences_registry.register
class FeedbackLimitStorageDays(PositiveIntegerPreference):
    section = 'Feedback'
    verbose_name = 'Maximum storage time (days) for feedbacks'
    name = "limit_storage_days"
    default = 360


@global_preferences_registry.register
class FeedbackLimitSize(PositiveIntegerPreference):
    section = 'Feedback'
    verbose_name = "Maximum feedback storage utilization (GB)"
    name = "limit_size"
    default = 100


@global_preferences_registry.register
class SymbolsLimitSize(PositiveIntegerPreference):
    section = 'Symbols'
    verbose_name = "Alert when symbol file storage exceeds (GB) "
    name = "limit_size"
    default = 100

@global_preferences_registry.register
class TimeZone(ChoicePreference):
    choices = [(tz, ' '.join([tz, datetime.now(pytz.timezone(tz)).strftime('%z')]))
               for tz in pytz.common_timezones]
    widget = Select2Widget
    section = 'Timezone'
    verbose_name = "Choose your timezone"
    name = "timezone"
    default = "UTC"


global_preferences = global_preferences_registry
global_preferences_manager = global_preferences.manager()
