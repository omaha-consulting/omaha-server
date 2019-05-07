from django.core.files.storage import DefaultStorage


class OverloadTestStorageMixin(object):
    """Mixin allows to overload FileField's storage.

    It can be useful when we use custom storages.
    For using setup the model attribute.
    """
    # ToDo: Add ability to work with models with more than 1 FileFields

    storage_class = DefaultStorage
    field_name = 'file'

    def setUp(self):
        self._file_field = self.model._meta.get_field(self.field_name)
        self._default_storage = self._file_field.storage
        test_storage = self.storage_class()
        self._file_field.storage = test_storage
        super(OverloadTestStorageMixin, self).setUp()

    def tearDown(self):
        self._file_field.storage = self._default_storage
        super(OverloadTestStorageMixin, self).tearDown()
