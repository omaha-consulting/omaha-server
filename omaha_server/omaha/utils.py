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

from functools import wraps
import datetime
import calendar

from singledispatch import singledispatch
from django_redis import get_redis_connection
from redis.exceptions import WatchError
from django.utils import timezone

from omaha.settings import KEY_PREFIX, KEY_LAST_ID

__all__ = ['get_sec_since_midnight', 'get_id']

redis = get_redis_connection('statistics')


def get_sec_since_midnight(date):
    """
    Return seconds since midnight

    >>> from datetime import datetime
    >>> get_sec_since_midnight(datetime(year=2014, month=1, day=1, second=42))
    42
    """
    midnight = date.replace(hour=0, minute=0, second=0, microsecond=0)
    delta = date - midnight
    return delta.seconds


def get_id(uuid):
    """
    >>> get_id('{8C65E04C-0383-4AE2-893F-4EC7C58F70DC}')
    1
    >>> get_id('{8C65E04C-0383-4AE2-893F-4EC7C58F70DC}')
    1
    """
    id = redis.get('{}:{}'.format(KEY_PREFIX, uuid))
    if id is None:
        id = create_id(uuid)
    return int(id)


def create_id(uuid):
    """
    >>> create_id('{8C65E04C-0383-4AE2-893F-4EC7C58F70DC}')
    1
    """
    with redis.pipeline() as pipe:
        while True:
            try:
                pipe.watch(KEY_LAST_ID)
                current_id = pipe.get(KEY_LAST_ID) or 0
                next_id = int(current_id) + 1
                pipe.multi()
                pipe.set(KEY_LAST_ID, next_id)
                pipe.execute()

                redis.set('{}:{}'.format(KEY_PREFIX, uuid), next_id)
                return next_id
            except WatchError:
                continue
            except:
                raise


def valuedispatch(func):
    _func = singledispatch(func)

    @wraps(func)
    def wrapper(*args, **kwargs):
        return _func.registry.get(args[0], _func)(*args, **kwargs)

    wrapper.register = _func.register
    wrapper.dispatch = _func.dispatch
    wrapper.registry = _func.registry
    return wrapper


def make_piechart(id, data, unit='users'):
    xdata = [i[0] for i in data]
    ydata = [i[1] for i in data]

    extra_serie = {
        "tooltip": {"y_start": "", "y_end": " " + unit},
    }
    chartdata = {'x': xdata, 'y1': ydata, 'extra1': extra_serie}
    charttype = "pieChart"
    chartcontainer = 'chart_container_%s' % id  # container name

    data = {
        'charttype': charttype,
        'chartdata': chartdata,
        'chartcontainer': chartcontainer,
        'extra': {
            'x_is_date': False,
            'x_axis_format': '',
            'tag_script_js': True,
            'jquery_on_ready': False,
        }
    }
    return data


def get_month_range_from_dict(source):
    """
    :param source: dictionary with keys 'start' and 'end
    :return: a tuple of datatime objects in the form (start, end)
    """
    now = timezone.now()
    start = source.get('start')

    end = source.get('end', datetime.datetime(now.year, now.month, calendar.monthrange(now.year, now.month)[1]))

    if not start:
        start = datetime.datetime(end.year-1, end.month+1, 1) if end.month != 12 else datetime.datetime(end.year, 1, 1)

    return start, end


def is_new_install(appid, userid):
    event = "known_users:{}"
    return not redis.getbit(event.format(appid), userid)
