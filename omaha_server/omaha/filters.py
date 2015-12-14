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

from django.forms import CharField

import django_filters
from django_select2.forms import HeavySelect2Widget

from omaha.models import AppRequest

EVENT_RESULT = {
    0: 'error',
    1: 'success',
    2: 'success reboot',
    3: 'success restart browser',
    4: 'cancelled',
    5: 'error installer MSI',
    6: 'error installer other',
    7: 'noupdate',
    8: 'error installer system',
    9: 'update deferred',
    10: 'handoff error',
}

EVENT_TYPE = {
    0: "unknown",
    1: "download complete",
    2: "install complete",
    3: "update complete",
    4: "uninstall",
    5: "download started",
    6: "install started",
    9: "new application install started",
    10: "setup started",
    11: "setup finished",
    12: "update application started",
    13: "update download started",
    14: "update download finished",
    15: "update installer started",
    16: "setup update begin",
    17: "setup update complete",
    20: "register product complete",
    30: "OEM install first check",
    40: "app-specific command started",
    41: "app-specific command ended",
    100: "setup failure",
    102: "COM server failure",
    103: "setup update failure",
}


# Python’s lambda is broken!
# http://math.andrej.com/2009/04/09/pythons-lambda-is-broken/

EVENT_RESULT_OPTIONS = dict([
    (k, (v.title(), (lambda k: lambda qs, name: qs.filter(events__eventresult=k+0))(k)))
    for k, v in EVENT_RESULT.items()
])

EVENT_TYPE_OPTIONS = dict([
    (k, (v.title(), (lambda k: lambda qs, name: qs.filter(events__eventtype=k+0))(k)))
    for k, v in EVENT_TYPE.items()
])

EVENT_RESULT_OPTIONS[''] = ('Any', lambda qs, name: qs.all())

EVENT_TYPE_OPTIONS[''] = ('Any', lambda qs, name: qs.all())


class EventResultFilter(django_filters.ChoiceFilter):
    options = EVENT_RESULT_OPTIONS

    def __init__(self, *args, **kwargs):
        kwargs['choices'] = [
            (key, value[0]) for key, value in self.options.items()]
        super(EventResultFilter, self).__init__(*args, **kwargs)

    def filter(self, qs, value):
        try:
            value = int(value)
        except (ValueError, TypeError):
            value = ''
        return self.options[value][1](qs, self.name)


class EventTypeFilter(django_filters.ChoiceFilter):
    options = EVENT_TYPE_OPTIONS

    def __init__(self, *args, **kwargs):
        kwargs['choices'] = [
            (key, value[0]) for key, value in self.options.items()]
        super(EventTypeFilter, self).__init__(*args, **kwargs)

    def filter(self, qs, value):
        try:
            value = int(value)
        except (ValueError, TypeError):
            value = ''
        return self.options[value][1](qs, self.name)


class FilterByUserIdWidget(HeavySelect2Widget):
    def build_attrs(self, extra_attrs=None, **kwargs):
        attrs = super(FilterByUserIdWidget, self).build_attrs(**kwargs)
        attrs['data-minimum-input-length'] = 2
        return attrs

    def _get_media(self):
        media = super(FilterByUserIdWidget, self)._get_media()
        override_index = media._js.index(u'django_select2/django_select2.js')
        media._js[override_index] = 'django-select2/js/select2_appid.js'
        return media

    media = property(_get_media)


class UserIdFilter(django_filters.Filter):
    field = CharField()


class AppRequestFilter(django_filters.FilterSet):
    request__created = django_filters.DateRangeFilter()
    event_type = EventTypeFilter()
    event_result = EventResultFilter()
    request__userid = django_filters.CharFilter(
        widget=FilterByUserIdWidget(data_view='select2_userid_filter'))

    class Meta:
        model = AppRequest
        fields = ('request__userid', 'request__created')
