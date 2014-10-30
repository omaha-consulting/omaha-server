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

from singledispatch import singledispatch
from redis_cache import get_redis_connection
from redis.exceptions import WatchError
from settings import KEY_PREFIX, KEY_LAST_ID

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
