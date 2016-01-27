# coding: utf8

"""
This software is licensed under the Apache 2 license, quoted below.

Copyright 2016 Crystalnix Limited

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

from functools import partial

from bitmapist import mark_event

from omaha.statistics import get_id, add_app_statistics

def collect_statistics(request, appid, channel, now=None):
    deviceID = request.GET.get('deviceID')
    version = request.GET.get('appVersionShort')
    if not deviceID or not version:
        return
    userid = get_id(deviceID)
    app = dict(appid=appid,
               version=version,
               tag=channel)
    mark_event('request', userid, now=now)

    add_app_statistics(userid, 'mac', app)
    update_live_statistics(userid, appid, version)


def update_live_statistics(userid, appid, version, now=None):
    mark = partial(mark_event, now=now, track_hourly=True)
    mark('online:{}:{}'.format(appid, version), userid)
    mark('online:{}:{}:{}'.format(appid, 'mac', version), userid)


