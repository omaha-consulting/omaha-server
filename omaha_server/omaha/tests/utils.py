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

import shutil
import tempfile
from django.conf import settings
from django.test import override_settings

from lxml.builder import E

class temporary_media_root(override_settings):
    """Temporarily override settings.MEDIA_ROOT with a temporary directory.

    The temporary directory is automatically created and destroyed.

    Use this function as a context manager:

    >>> from django_downloadview.test import temporary_media_root
    >>> from django.conf import settings  # NoQA
    >>> global_media_root = settings.MEDIA_ROOT
    >>> with temporary_media_root():
    ...     global_media_root == settings.MEDIA_ROOT
    False
    >>> global_media_root == settings.MEDIA_ROOT
    True

    Or as a decorator:

    >>> @temporary_media_root()
    ... def use_temporary_media_root():
    ...     return settings.MEDIA_ROOT
    >>> tmp_media_root = use_temporary_media_root()
    >>> global_media_root == tmp_media_root
    False
    >>> global_media_root == settings.MEDIA_ROOT
    True

    """

    def enable(self):
        """Create a temporary directory and use it to override
        settings.MEDIA_ROOT."""
        tmp_dir = tempfile.mkdtemp()
        self.options['MEDIA_ROOT'] = tmp_dir
        super(temporary_media_root, self).enable()

    def disable(self):
        """Remove directory settings.MEDIA_ROOT then restore original
        setting."""
        shutil.rmtree(settings.MEDIA_ROOT)
        super(temporary_media_root, self).disable()


def create_app_xml(**kwargs):
    events = kwargs.pop('events', [])
    app = dict(**kwargs)
    app = E.app(app)
    if type(events) is not list:
        events = [events]
    for event in events:
        e = E.event(event)
        app.append(e)
    return app
