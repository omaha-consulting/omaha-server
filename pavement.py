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

from raven import Client
from paver.easy import task, needs
from paver.easy import sh


client = Client(os.environ.get('RAVEN_DNS'))


@task
def test():
    sh('./manage.py test --settings=omaha_server.settings_test', cwd='omaha_server')


@task
def test_tox():
    path_to_test = os.getenv("PATH_TO_TEST", '')
    settings = os.getenv("DJANGO_SETTINGS_MODULE", 'omaha_server.settings_test')
    sh('./manage.py test %s --settings=%s' % (path_to_test, settings), cwd='omaha_server')


@task
def test_postgres():
    sh('./manage.py test --settings=omaha_server.settings_test_postgres', cwd='omaha_server')


@task
@needs('test', 'test_postgres')
def test_all():
    pass


@task
def up_local_dev_server():
    """
    Requirements:

    - [docker](docker.com) or [boot2docker](https://github.com/boot2docker/boot2docker) for OS X or Windows
    - [docker-compose](https://docs.docker.com/compose/install/)

    """
    sh('docker-compose -f docker-compose.dev.yml -p dev up -d db')
    sh('docker-compose -f docker-compose.dev.yml -p dev up -d web')
    print("""Open http://{DOCKER_HOST}:9090/admin/\n username: admin\n password: admin""")


@task
def deploy_dev():
    sh('ebs-deploy deploy -e omaha-server-dev', cwd='omaha_server')


@task
def collectstatic():
    sh('./manage.py collectstatic --noinput', cwd='omaha_server')


@task
def loaddata():
    sh('./manage.py loaddata fixtures/initial_data.json', cwd='omaha_server')


@task
def migrate():
    sh('./manage.py migrate auth --noinput', cwd='omaha_server')
    sh('./manage.py migrate --noinput', cwd='omaha_server')


@task
def create_admin():
    sh('./createadmin.py', cwd='omaha_server')

@task
def docker_run():
    try:
        is_private = True if os.environ.get('OMAHA_SERVER_PRIVATE', '').title() == 'True' else False

        if is_private:
            migrate()
            loaddata()
            create_admin()
            collectstatic()

        sh('/usr/bin/supervisord')
    except:
        client.captureException()
        raise


@task
def docker_run_test():
    sh('apt-get install -y python-dev libxslt-dev libpq-dev')
    sh('pip install -r requirements/test.txt --use-mirrors')
    test()
    test_postgres()


@task
def run_test_in_docker():
    try:
        sh('docker-compose -f docker-compose.test.yml -p omaha_testing run --rm web paver docker_run_test')
    except:
        pass
    sh('docker-compose -f docker-compose.test.yml -p omaha_testing stop')
    sh('docker-compose -f docker-compose.test.yml -p omaha_testing rm --force')
