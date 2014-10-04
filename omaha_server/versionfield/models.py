# coding: utf8

import sys

if 'test' in sys.argv:  # pragma: no cover
    from django.db import models
    from . import VersionField


    class DummyModel(models.Model):
        version = VersionField()


    class DummyModelCustomBit(models.Model):
        version = VersionField(number_bits=(8, 16, 8))
