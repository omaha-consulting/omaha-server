# coding: utf8

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
    id = redis.get('{}:{}'.format(KEY_PREFIX, uuid))
    if id is None:
        id = create_id(uuid)
    return int(id)


def create_id(uuid):
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
