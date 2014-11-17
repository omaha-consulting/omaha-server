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

from paver.easy import task
from paver.easy import sh


@task
def test():
    sh('./manage.py test --settings=omaha_server.settings_test', cwd='omaha_server')


@task
def up_local_dev_server():
    """
    Requirements:

    - [docker](docker.com) or [boot2docker](https://github.com/boot2docker/boot2docker) for OS X or Windows
    - [fig](fig.sh)

    """
    sh('fig up -d db')
    sh('fig up -d web')
    print """Open http://{DOCKER_HOST}:9090/admin/\n username: admin\n password: admin"""


@task
def deploy_dev():
    sh('ebs-deploy deploy -e omaha-server-dev', cwd='omaha_server')


@task
def collectstatic():
    sh('./manage.py collectstatic --noinput', cwd='omaha_server')


@task
def migrate():
    sh('./manage.py migrate --noinput', cwd='omaha_server')


@task
def create_admin():
    sh('./createadmin.py', cwd='omaha_server')


@task
def docker_run():
    migrate()
    create_admin()
    collectstatic()
    sh('/usr/bin/supervisord')


@task
def docker_run_test():
    sh('pip install -r requirements-test.txt --use-mirrors')
    test()


@task
def run_test_in_docker():
    sh('fig run --rm web paver docker_run_test')
