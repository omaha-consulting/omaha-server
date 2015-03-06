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

from lxml import etree, objectify


__all__ = ['parser', 'parse_request']


BASE_DIR = os.path.dirname(__file__)

with open(os.path.join(BASE_DIR, 'request.xsd')) as f:
    schema = etree.XMLSchema(file=f)

parser = objectify.makeparser(schema=schema)


def parse_request(request):
    """
        >>> request = b'''<?xml version="1.0" encoding="UTF-8"?>
        ... <request protocol="3.0"
        ...          version="1.3.23.0"
        ...          ismachine="0"
        ...          sessionid="{5FAD27D4-6BFA-4daa-A1B3-5A1F821FEE0F}"
        ...          userid="{D0BBD725-742D-44ae-8D46-0231E881D58E}"
        ...          installsource="scheduler"
        ...          testsource="ossdev"
        ...          requestid="{C8F6EDF3-B623-4ee6-B2DA-1D08A0B4C665}">
        ...     <os platform="win" version="6.1" sp="" arch="x64"/>
        ...     <app appid="{430FD4D0-B729-4F61-AA34-91526481799D}" version="1.2.23.0" nextversion="" lang="en" brand="GGLS"
        ...          client="someclientid" installage="39">
        ...         <updatecheck/>
        ...         <ping r="1"/>
        ...     </app>
        ...     <app appid="{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}" version="2.2.2.0" nextversion="" lang="en" brand="GGLS"
        ...          client="" installage="6">
        ...         <updatecheck/>
        ...         <ping r="1"/>
        ...     </app>
        ... </request>'''
        >>> request_obj = parse_request(request)
        >>> request_obj.get('version')
        '1.3.23.0'
        >>> request_obj.os.get('platform')
        'win'
        >>> request_obj.app.get('appid')
        '{430FD4D0-B729-4F61-AA34-91526481799D}'
        >>> request_obj.app.find('updatecheck')
        ''
        >>> request_obj.keys()
        ['protocol', 'version', 'ismachine', 'sessionid', 'userid', 'installsource', 'testsource', 'requestid']
        >>> request_obj.values()
        ['3.0', '1.3.23.0', '0', '{5FAD27D4-6BFA-4daa-A1B3-5A1F821FEE0F}', '{D0BBD725-742D-44ae-8D46-0231E881D58E}', 'scheduler', 'ossdev', '{C8F6EDF3-B623-4ee6-B2DA-1D08A0B4C665}']
        >>> request_obj.tag
        'request'
        >>> for app in request_obj.find('app'):
        ...     app.get('appid')
        ...
        '{430FD4D0-B729-4F61-AA34-91526481799D}'
        '{D0AB2EBC-931B-4013-9FEB-C9C4C2225C8C}'
    """
    return objectify.fromstring(request, parser)
