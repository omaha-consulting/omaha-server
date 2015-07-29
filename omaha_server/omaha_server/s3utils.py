from storages.backends.s3boto import S3BotoStorage
from furl import furl


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

    def url(self, name):
        url = super(StaticS3Storage, self).url(name)
        if name.endswith('/') and not url.endswith('/'):
            url += '/'
        return url


class S3Storage(BaseS3Storage):
    pass
