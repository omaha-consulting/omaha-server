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

from __future__ import unicode_literals

from datetime import datetime

from lxml.builder import E

from omaha.utils import get_sec_since_midnight


__all__ = [
    'Response', 'Url', 'Urls', 'Package', 'Packages',
    'Action', 'Actions', 'Manifest', 'App', 'Updatecheck',
    'Updatecheck_positive', 'Updatecheck_negative',
]


def Response(apps_list, protocol='3.0', date=None, server='prod'):
    elapsed_seconds = get_sec_since_midnight(date or datetime.utcnow())
    resp = E.response(
        dict(protocol=protocol, server=server),
        E.daystart(elapsed_seconds=str(elapsed_seconds)),
    )
    list(map(resp.append, apps_list))
    return resp


def Ping(status='ok'):
    """
        >>> from lxml import etree as ET
        >>> ET.tostring(Ping())
        b'<ping status="ok"/>'
    """
    return E.ping(dict(status=status))


def Event(status='ok'):
    """
        >>> from lxml import etree as ET
        >>> ET.tostring(Event())
        b'<event status="ok"/>'
    """
    return E.event(dict(status=status))


def Data(name, status='ok', index=None, text=None):
    """
        >>> from lxml import etree as ET
        >>> ET.tostring(Data('untrusted'))
        b'<data status="ok" name="untrusted"/>'
        >>> ET.tostring(Data('install', index='verboselogging', text='app-specific values here'))
        b'<data status="ok" index="verboselogging" name="install">app-specific values here</data>'
    """
    attrs = dict(
        name=name,
        status=status,
    )
    if index:
        attrs['index'] = index
    data = E.data(attrs)
    data.text = text
    return data


def Url(url):
    """
        >>> from lxml import etree as ET
        >>> ET.tostring(Url('http://cache.pack.google.com/edgedl/chrome/install/782.112/'))
        b'<url codebase="http://cache.pack.google.com/edgedl/chrome/install/782.112/"/>'
    """
    return E.url(dict(codebase=url))


def Urls(urls_list):
    """
        >>> from lxml import etree as ET
        >>> print(ET.tostring(Urls(['http://cache.pack.google.com/edgedl/chrome/install/782.112/',
        ...                   'http://cdn.pack.google.com/edgedl/chrome/install/782.112/']), pretty_print=True))
        <urls>
          <url codebase="http://cache.pack.google.com/edgedl/chrome/install/782.112/"/>
          <url codebase="http://cdn.pack.google.com/edgedl/chrome/install/782.112/"/>
        </urls>
    """
    urls = E.urls()
    list(map(lambda url: urls.append(Url(url)), urls_list))
    return urls


def Package(name, required, size, hash, fp=None):
    """
        >>> from lxml import etree as ET
        >>> print(ET.tostring(Package(
        ... 'chrome_installer.exe',
        ... required='true',
        ... size='23963192',
        ... hash='VXriGUVI0TNqfLlU02vBel4Q3Zo=')))
        b'<package required="true" hash="VXriGUVI0TNqfLlU02vBel4Q3Zo=" name="chrome_installer.exe" size="23963192"/>'
    """
    attrs = dict(
        name=name,
        required=required,
        size=size,
        hash=hash
    )
    if fp:
        attrs['fp'] = fp
    package = E.package(attrs)
    return package


def Packages(packages_list):
    """
        >>> from lxml import etree as ET
        >>> print(ET.tostring(Packages([Package(
        ... 'chrome_installer.exe',
        ... required='true',
        ... size='23963192',
        ... hash='VXriGUVI0TNqfLlU02vBel4Q3Zo=')]), pretty_print=True))
        b'<packages>
          <package required="true" hash="VXriGUVI0TNqfLlU02vBel4Q3Zo=" name="chrome_installer.exe" size="23963192"/>
        </packages>'
    """
    packages = E.packages()
    list(map(packages.append, packages_list))
    return packages


def Action(event, **kwargs):
    """
        >>> from lxml import etree as ET
        >>> ET.tostring(Action('install', run='chrome_installer.exe', arguments='--do-not-launch-chrome'))
        b'<action run="chrome_installer.exe" event="install" arguments="--do-not-launch-chrome"/>'
    """
    attrs = dict(event=event)
    attrs.update(
        kwargs
    )
    return E.action(attrs)


def Actions(actions_list):
    """
        >>> from lxml import etree as ET
        >>> ET.tostring(Actions([Action('install', run='chrome_installer.exe', arguments='--do-not-launch-chrome')]))
        b'<actions><action run="chrome_installer.exe" event="install" arguments="--do-not-launch-chrome"/></actions>'
    """
    actions = E.actions()
    list(map(actions.append, actions_list))
    return actions


def Manifest(version, packages, actions=None):
    """
        >>> from lxml import etree as ET
        >>> print(ET.tostring(Manifest(
        ... "13.0.782.112",
        ... packages=Packages([Package(
        ...     'chrome_installer.exe',
        ...     required='true',
        ...     size='23963192',
        ...     hash='VXriGUVI0TNqfLlU02vBel4Q3Zo=')])
        ... ), pretty_print=True))
        b'<manifest version="13.0.782.112">
          <packages>
            <package required="true" hash="VXriGUVI0TNqfLlU02vBel4Q3Zo=" name="chrome_installer.exe" size="23963192"/>
          </packages>
        </manifest>'
    """
    manifest = E.manifest(
        dict(version=version),
        packages
    )
    if actions is not None:
        manifest.append(actions)
    return manifest


def Updatecheck(status='noupdate', urls=None, manifest=None):
    updatecheck = E.updatecheck(
        dict(status=status)
    )
    if urls is not None:
        updatecheck.append(urls)
    if manifest is not None:
        updatecheck.append(manifest)
    return updatecheck


def Updatecheck_negative():
    """
        >>> from lxml import etree as ET
        >>> ET.tostring(Updatecheck_negative())
        b'<updatecheck status="noupdate"/>'
    """
    return Updatecheck()


def Updatecheck_positive(urls, manifest):
    """
        >>> from lxml import etree as ET
        >>> manifest = Manifest(
        ...     version='13.0.782.112',
        ...     packages=Packages([Package(
        ...         name='chrome_installer.exe',
        ...         required='true',
        ...         size='23963192',
        ...         hash='VXriGUVI0TNqfLlU02vBel4Q3Zo=',
        ...     )]),
        ...     actions=Actions([
        ...         Action(event='install', arguments='--do-not-launch-chrome', run='chrome_installer.exe'),
        ...         Action(event='postinstall', version='13.0.782.112', onsuccess='exitsilentlyonlaunchcmd'),
        ...     ])
        ... )
        >>> urls=['http://cache.pack.google.com/edgedl/chrome/install/782.112/']
        >>> print(ET.tostring(Updatecheck_positive(urls, manifest), pretty_print=True))
        b'<updatecheck status="ok">
          <urls>
            <url codebase="http://cache.pack.google.com/edgedl/chrome/install/782.112/"/>
          </urls>
          <manifest version="13.0.782.112">
            <packages>
              <package required="true" hash="VXriGUVI0TNqfLlU02vBel4Q3Zo=" name="chrome_installer.exe" size="23963192"/>
            </packages>
            <actions>
              <action run="chrome_installer.exe" event="install" arguments="--do-not-launch-chrome"/>
              <action version="13.0.782.112" event="postinstall" onsuccess="exitsilentlyonlaunchcmd"/>
            </actions>
          </manifest>
        </updatecheck>'
    """
    return Updatecheck(status='ok', urls=Urls(urls), manifest=manifest)


def App(app_id, status='ok', experiments='', updatecheck=None, ping=False,
        events=None, data_list=None):
    attrs = dict(appid=app_id, status=status)
    if experiments:
        attrs['experiments'] = experiments
    app = E.app(attrs)
    list(map(app.append, events or []))
    list(map(app.append, data_list or []))
    if updatecheck is not None:
        app.append(updatecheck)
    if ping:
        app.append(Ping())
    return app
