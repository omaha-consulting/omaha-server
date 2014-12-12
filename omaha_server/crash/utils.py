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

from clom import clom

from settings import MINIDUMP_STACKWALK_PATH, SYMBOLS_PATH


class FileNotFoundError(Exception):
    pass


minidump_stackwalk = clom[MINIDUMP_STACKWALK_PATH].with_opts('-m')


def get_stacktrace(crashdump_path):
    if not os.path.isfile(crashdump_path):
        raise FileNotFoundError

    rezult = minidump_stackwalk(crashdump_path, SYMBOLS_PATH).shell()
    return rezult, rezult.stderr
