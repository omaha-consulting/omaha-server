from storages.backends.s3boto import S3BotoStorage
from furl import furl

from django.utils.module_loading import import_string
from django.conf import settings


class BaseS3Storage(S3BotoStorage):
    def url(self, name):
        url = super(BaseS3Storage, self).url(name)
        if not self.querystring_auth:
            f = furl(url)
            if 'x-amz-security-token' in f.args:
                del f.args['x-amz-security-token']
                url = f.url
        return url


class StaticS3Storage(BaseS3Storage):
    location = 'static'
    default_acl = 'public-read'

    def url(self, name):
        url = super(StaticS3Storage, self).url(name)
        if name.endswith('/') and not url.endswith('/'):
            url += '/'
        return url


class PublicReadS3Storage(BaseS3Storage):
    querystring_auth = False
    default_acl = 'public-read'


class S3Storage(BaseS3Storage):
    pass


def get_public_read_storage_class():
    return import_string(getattr(settings, 'PUBLIC_READ_FILE_STORAGE', settings.DEFAULT_FILE_STORAGE))


public_read_storage = get_public_read_storage_class()()
