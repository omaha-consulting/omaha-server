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

import os
import re

from clom import clom

from settings import MINIDUMP_STACKWALK_PATH, SYMBOLS_PATH
from stacktrace_to_json import pipe_dump_to_json_dump


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
    elif 'file' in frame and 'line' in frame:
        signature = '%s#%d' % (frame['file'], frame['line'])
    elif 'module' in frame and 'module_offset' in frame:
        signature = '%s@%s' % (frame['module'], frame['module_offset'])
    else:
        signature = '@%s' % frame['offset']
    frame['signature'] = signature
    frame['short_signature'] = re.sub('\(.*\)', '', signature)
    return frame


def parse_stacktrace(stacktrace):
    stacktrace_dict = pipe_dump_to_json_dump(str(stacktrace).splitlines())
    stacktrace_dict['crashing_thread']['frames'] = map(add_signature_to_frame, stacktrace_dict['crashing_thread']['frames'])
    return stacktrace_dict


def get_signature(stacktrace):
    try:
        frame = stacktrace['crashing_thread']['frames'][0]
        signature = frame['signature']
    except KeyError, IndexError:
        signature = 'EMPTY: no frame data available'
    return signature
