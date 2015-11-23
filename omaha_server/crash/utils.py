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

from builtins import str

import os
import re

from django.conf import settings

from clom import clom
from raven import Client

from crash.settings import MINIDUMP_STACKWALK_PATH, SYMBOLS_PATH
from crash.stacktrace_to_json import pipe_dump_to_json_dump


client = Client(getattr(settings, 'RAVEN_DSN_STACKTRACE', None))


class FileNotFoundError(Exception):
    pass


minidump_stackwalk = clom[MINIDUMP_STACKWALK_PATH].with_opts('-m')


def get_stacktrace(crashdump_path):
    if not os.path.isfile(crashdump_path):
        raise FileNotFoundError

    rezult = minidump_stackwalk(crashdump_path, SYMBOLS_PATH).shell()
    return rezult, rezult.stderr


def add_signature_to_frame(frame):
    frame = frame.copy()
    if 'function' in frame:
        # Remove spaces before all stars, ampersands, and commas
        function = re.sub(' (?=[\*&,])', '', frame['function'])
        # Ensure a space after commas
        function = re.sub(',(?! )', ', ', function)
        frame['function'] = function
        signature = function
    elif 'abs_path' in frame and 'lineno' in frame:
        signature = '%s#%d' % (frame['abs_path'], frame['lineno'])
    elif 'filename' in frame and 'module_offset' in frame:
        signature = '%s@%s' % (frame['filename'], frame['module_offset'])
    else:
        signature = '@%s' % frame['offset']
    frame['signature'] = signature
    frame['short_signature'] = re.sub('\(.*\)', '', signature)
    return frame


def parse_stacktrace(stacktrace):
    stacktrace_dict = pipe_dump_to_json_dump(str(stacktrace).splitlines())
    stacktrace_dict['crashing_thread']['frames'] = list(
        map(add_signature_to_frame,
            stacktrace_dict['crashing_thread']['frames']))
    return dict(stacktrace_dict)


def get_signature(stacktrace):
    try:
        frame = stacktrace['crashing_thread']['frames'][0]
        signature = frame['signature']
    except (KeyError, IndexError):
        signature = 'EMPTY: no frame data available'
    return signature


def send_stacktrace_sentry(crash):
    stacktrace = crash.stacktrace_json

    exception = {
        "values": [
            {
                "type": stacktrace.get('crash_info', {}).get('type', 'unknown exception'),
                "value": stacktrace.get('crash_info', {}).get('crash_address', '0x0'),
                "stacktrace": stacktrace['crashing_thread']
            }
        ]
    }

    data = {'sentry.interfaces.Exception': exception}

    if crash.userid:
        data['sentry.interfaces.User'] = dict(id=crash.userid)

    extra = dict(
        crash_admin_panel_url='http://{}{}'.format(
            settings.HOST_NAME,
            '/admin/crash/crash/%s/' % crash.pk),
        crashdump_url=crash.upload_file_minidump.url,
    )

    if crash.meta:
        extra.update(crash.meta)

    if crash.archive:
        extra['archive_url'] = crash.archive.url

    tags = {}
    tags.update(stacktrace.get('system_info', {}))

    if crash.appid:
        tags['appid'] = crash.appid

    client.capture(
        'raven.events.Message',
        message=crash.signature,
        extra=extra,
        tags=tags,
        data=data
    )


def parse_debug_meta_info(head, exception=Exception):
    head = head.decode()
    head_list = head.split(' ', 4)
    if head_list[0] != 'MODULE':
        raise exception(u"The file contains invalid data.")
    return dict(debug_id=head_list[-2],
                debug_file=head_list[-1])
