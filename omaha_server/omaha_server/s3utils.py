from storages.backends.s3boto import S3BotoStorage

class StaticS3Storage(S3BotoStorage):
    location = 'static'

    def url(self, name):
        url = super(StaticS3Storage, self).url(name)
        if name.endswith('/') and not url.endswith('/'):
            url += '/'
        return url
