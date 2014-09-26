# coding: utf8

from datetime import datetime

from lxml.builder import E

from utils import get_sec_since_midnight


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
    map(resp.append, apps_list)
    return resp


def Ping(status='ok'):
    return E.ping(dict(status=status))


def Event(status='ok'):
    return E.event(dict(status=status))


def Url(url):
    return E.url(dict(codebase=url))


def Urls(urls_list):
    urls = E.urls()
    map(lambda url: urls.append(Url(url)), urls_list)
    return urls


def Package(name, required, size, hash, fp=None):
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
    packages = E.packages()
    map(packages.append, packages_list)
    return packages


def Action(event, **kwargs):
    attrs_optional_name = ('version', 'successurl', 'terminateallbrowsers',
                           'successsaction', 'onsuccess', 'arguments', 'run')
    attrs = dict(
        event=event
    )

    attrs.update(
        dict([(key, val) for key, val in kwargs.iteritems() if key in attrs_optional_name])
    )

    action = E.action(attrs)
    return action


def Actions(actions_list):
    actions = E.actions()
    map(actions.append, actions_list)
    return actions


def Manifest(version, packages, actions=None):
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
    return Updatecheck()


def Updatecheck_positive(urls, manifest):
    return Updatecheck(status='ok', urls=Urls(urls), manifest=manifest)


def App(app_id, status='ok', experiments='', updatecheck=None, ping=False, events=None):
    attrs = dict(appid=app_id, status=status)
    if experiments:
        attrs['experiments'] = experiments
    app = E.app(attrs)
    map(app.append, events or [])
    if updatecheck is not None:
        app.append(updatecheck)
    if ping:
        app.append(Ping())
    return app
