from itertools import chain
import operator
import time

from django.db.models.loading import get_model
from django.utils import timezone
from django.conf import settings
from django.db.models import Count
from django.core.cache import cache

import boto
from raven import Client

from omaha.models import Version as OmahaVersion
from omaha.utils import valuedispatch
from sparkle.models import SparkleVersion
from crash.models import Crash, Symbols
from feedback.models import Feedback

from dynamic_preferences_registry import global_preferences_manager as gpm

dsn = getattr(settings, 'RAVEN_CONFIG', None)
if dsn:
    dsn = dsn['dsn']
raven = Client(dsn, list_max_length=1000)


@valuedispatch
def bulk_delete(cls, qs):
    raise NotImplementedError


@bulk_delete.register(Crash)
def _(cls, qs):
    if settings.DEFAULT_FILE_STORAGE == 'storages.backends.s3boto.S3BotoStorage':
        qs = s3_bulk_delete(qs, file_fields=['archive', 'upload_file_minidump'],
                            s3_fields=['minidump_archive', 'minidump'])

    result = dict()
    result['count'] = qs.count()
    result['size'] = qs.get_size()
    result['elements'] = list(qs.values_list('id', 'created', 'signature'))
    created_to_string = lambda x: 'Created: %s' % x.strftime("%d. %B %Y %I:%M%p")
    signature_to_string = lambda x: 'Signature: %s' % x
    result['elements'] = map(lambda x: (x[0], created_to_string(x[1]), signature_to_string(x[2])), result['elements'])
    qs.delete()
    return result


@bulk_delete.register(Feedback)
def _(cls, qs):
    if settings.DEFAULT_FILE_STORAGE == 'storages.backends.s3boto.S3BotoStorage':
        qs = s3_bulk_delete(qs, file_fields=['attached_file', 'blackbox', 'screenshot', 'system_logs'],
                            s3_fields=['feedback_attach', 'blackbox', 'screenshot', 'system_logs'])

    result = dict()
    result['count'] = qs.count()
    result['size'] = qs.get_size()
    result['elements'] = list(qs.values_list('id', 'created'))
    created_to_string = lambda x: 'Created: %s' % x.strftime("%d. %B %Y %I:%M%p")
    result['elements'] = map(lambda x: (x[0], created_to_string(x[1])), result['elements'])
    qs.delete()
    return result


@bulk_delete.register(Symbols)
def _(cls, qs):
    if settings.DEFAULT_FILE_STORAGE == 'storages.backends.s3boto.S3BotoStorage':
        qs = s3_bulk_delete(qs, file_fields=['file'], s3_fields=['symbols'])

    result = dict()
    result['count'] = qs.count()
    result['size'] = qs.get_size()
    result['elements'] = list(qs.values_list('id', 'created'))
    created_to_string = lambda x: 'Created: %s' % x.strftime("%d. %B %Y %I:%M%p")
    result['elements'] = map(lambda x: (x[0], created_to_string(x[1])), result['elements'])
    qs.delete()
    return result


@bulk_delete.register(OmahaVersion)
def _(cls, qs):
    if settings.DEFAULT_FILE_STORAGE == 'storages.backends.s3boto.S3BotoStorage':
        qs = s3_bulk_delete(qs, file_fields=['file'], s3_fields=['build'])

    result = dict()
    result['count'] = qs.count()
    result['size'] = qs.get_size()
    result['elements'] = list(qs.values_list('id', 'created'))
    created_to_string = lambda x: 'Created: %s' % x.strftime("%d. %B %Y %I:%M%p")
    result['elements'] = map(lambda x: (x[0], created_to_string(x[1])), result['elements'])
    qs.delete()
    return result


@bulk_delete.register(SparkleVersion)
def _(cls, qs):
    if settings.DEFAULT_FILE_STORAGE == 'storages.backends.s3boto.S3BotoStorage':
        qs = s3_bulk_delete(qs, file_fields=['file'], s3_fields=['sparkle'])

    result = dict()
    result['count'] = qs.count()
    result['size'] = qs.get_size()
    result['elements'] = list(qs.values_list('id', 'created'))
    created_to_string = lambda x: 'Created: %s' % x.strftime("%d. %B %Y %I:%M%p")
    result['elements'] = map(lambda x: (x[0], created_to_string(x[1])), result['elements'])
    qs.delete()
    return result


def s3_bulk_delete(qs, file_fields, s3_fields):
    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)

    file_keys = qs.values_list(*file_fields)
    file_keys = [key for key in chain(*file_keys) if key]
    bucket.delete_keys(file_keys)
    s3_keys = [x for x in chain(*[bucket.list(prefix="%s/" % field) for field in s3_fields])]
    error_keys = filter(lambda key: key in s3_keys, file_keys)
    if error_keys:
        exclude_fields = [qs.exclude(**{"%s__in" % key: error_keys}) for key in file_fields]
        qs = reduce(operator.and_, exclude_fields)

    update_kwargs = dict(zip(file_fields, [None for x in file_fields]))
    qs.update(**update_kwargs)
    return qs


def delete_older_than(app, model_name, limit=None):
    if not limit:
        preference_key = '__'.join([model_name, 'limit_storage_days'])
        limit = gpm[preference_key]
    model = get_model(app, model_name)
    offset = timezone.timedelta(days=limit)
    limit = timezone.now() - offset
    old_objects = model.objects.filter(created__lte=limit)
    result = dict()
    if old_objects:
        result = bulk_delete(model, old_objects)
    return result


def delete_duplicate_crashes(limit=None):
    full_result = dict(count=0, size=0, signatures=dict(), elements=[])
    if not limit:
        preference_key = '__'.join(['Crash', 'duplicate_number'])
        limit = gpm[preference_key]
    duplicated = Crash.objects.values('signature').annotate(count=Count('signature'))
    duplicated = filter(lambda x: x['count'] > limit, duplicated)
    for group in duplicated:
        qs = Crash.objects.filter(signature=group['signature'])
        dup_elements = []
        dup_count = qs.count()
        while dup_count > limit:
            bulk_size = dup_count - limit if dup_count - limit < 1000 else 1000
            bulk_ids = qs[:bulk_size].values_list('id', flat=True)
            bulk = qs.filter(id__in=bulk_ids)
            result = bulk_delete(Crash, bulk)
            full_result['count'] += result['count']
            full_result['size'] += result['size']
            full_result['elements'] += result['elements']
            dup_elements += result['elements']
            dup_count -= bulk_size
        full_result['signatures'].update({'%s' % (group['signature'],): dup_elements})
    return full_result


def delete_size_is_exceeded(app, model_name, limit=None):
    if not limit:
        preference_key = '__'.join([model_name, 'limit_size'])
        limit = gpm[preference_key] * 1024 * 1024 * 1024
    else:
        limit *= 1024*1024*1024
    model = get_model(app, model_name)
    group_count = 1000
    full_result = dict(count=0, size=0, elements=[])
    objects_size = model.objects.get_size()

    while objects_size > limit:
        group_objects_ids = list(model.objects.order_by('created').values_list("id", flat=True)[:group_count])
        group_objects = model.objects.order_by('created').filter(pk__in=group_objects_ids)
        group_size = group_objects.get_size()
        diff_size = objects_size - limit

        if group_size > diff_size:
            group_size = 0
            low_border = 0
            for instance in group_objects:
                group_size += instance.size
                low_border += 1
                if group_size >= diff_size:
                    group_objects = model.objects.order_by('created').filter(pk__in=group_objects_ids[:low_border])
                    break

        result = bulk_delete(model, group_objects)
        objects_size -= result['size']
        full_result['count'] += result['count']
        full_result['size'] += result['size']
        full_result['elements'] += result['elements']
    return full_result


def monitoring_size():
    size = OmahaVersion.objects.get_size()
    if size > gpm['Version__limit_size'] * 1024 * 1024 * 1024:
        raven.captureMessage("[Limitation]Size limit of omaha versions is exceeded. Current size is %.4f GB[%d]" % (float(size) / 1024 / 1024 / 1024, time.time()),
                             data={'level': 30, 'logger': 'limitation'})
    cache.set('omaha_version_size', size)

    size = SparkleVersion.objects.get_size()
    if size > gpm['SparkleVersion__limit_size'] * 1024 * 1024 * 1024:
        raven.captureMessage("[Limitation]Size limit of sparkle versions is exceeded. Current size is %.4f GB[%d]" % (float(size) / 1024 / 1024 / 1024, time.time()),
                             data={'level': 30, 'logger': 'limitation'})
    cache.set('sparkle_version_size', size)

    size = Feedback.objects.get_size()
    if size > gpm['Feedback__limit_size'] * 1024 * 1024 * 1024:
        raven.captureMessage("[Limitation]Size limit of feedbacks is exceeded. Current size is %.4f GB[%d]" % (float(size) / 1024 / 1024 / 1024, time.time()),
                             data={'level': 30, 'logger': 'limitation'})
    cache.set('feedbacks_size', size)

    size = Crash.objects.get_size()
    if size > gpm['Crash__limit_size'] * 1024 * 1024 * 1024:
        raven.captureMessage("[Limitation]Size limit of crashes is exceeded. Current size is %.4f GB[%d]" % (float(size) / 1024 / 1024 / 1024, time.time()),
                             data={'level': 30, 'logger': 'limitation'})
    cache.set('crashes_size', size)

    size = Symbols.objects.get_size()
    if size > gpm['Symbols__limit_size'] * 1024 * 1024 * 1024:
        raven.captureMessage("[Limitation]Size limit of symbols is exceeded. Current size is %.4f GB[%d]" % (float(size) / 1024 / 1024 / 1024, time.time()),
                             data={'level': 30, 'logger': 'limitation'})
    cache.set('symbols_size', size)
