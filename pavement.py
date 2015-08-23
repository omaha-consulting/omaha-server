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
from paver.easy import task
from paver.easy import sh


client = Client(os.environ.get('RAVEN_DNS'))


@task
def test():
    sh('./manage.py test --settings=omaha_server.settings_test', cwd='omaha_server')


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
def create_db_public_user():
    import psycopg2

    db_public_user = os.environ['DB_PUBLIC_USER']
    db_public_password = os.environ['DB_PUBLIC_PASSWORD']

    conn = psycopg2.connect(host=os.environ['DB_HOST'],
                          user=os.environ['DB_USER'],
                          password=os.environ['DB_PASSWORD'],
                          database=os.environ['DB_NAME'])
    curs = conn.cursor()

    try:
        # user and group
        curs.execute("CREATE USER %s WITH PASSWORD '%s';" % (db_public_user, db_public_password))
        curs.execute('CREATE GROUP public_users WITH USER %s;' % db_public_user)

        # versions
        curs.execute('GRANT SELECT ON TABLE applications, platforms, platforms_id_seq, '
                     'channels, channels_id_seq, versions, versions_id_seq, actions, '
                     'actions_id_seq, omaha_data, omaha_data_id_seq, omaha_partialupdate, '
                     'omaha_partialupdate_id_seq, sparkle_sparkleversion, '
                     'sparkle_sparkleversion_id_seq TO GROUP public_users;')

        # crash
        curs.execute('GRANT SELECT, INSERT, UPDATE ON TABLE crash_crash, crash_crash_id_seq, '
                     'crash_crashdescription, crash_crashdescription_id_seq TO GROUP public_users;')
        curs.execute('GRANT SELECT ON TABLE crash_symbols, crash_symbols_id_seq TO GROUP public_users;')
        curs.execute('GRANT INSERT ON TABLE feedback_feedback, feedback_feedback_id_seq TO GROUP public_users;')

        # statistics
        curs.execute('GRANT SELECT, INSERT, UPDATE ON TABLE omaha_apprequest, '
                     'omaha_apprequest_id_seq, omaha_apprequest_events, '
                     'omaha_apprequest_events_id_seq, omaha_event, omaha_event_id_seq, omaha_hw, '
                     'omaha_hw_id_seq, omaha_os, omaha_os_id_seq, omaha_request, '
                     'omaha_request_id_seq TO GROUP public_users;')

        # dev
        curs.execute('GRANT INSERT ON TABLE httplog_entry, httplog_entry_id_seq TO GROUP public_users;')
        conn.commit()
    except psycopg2.ProgrammingError:
        pass
    finally:
        curs.close()
        conn.close()


@task
def docker_run():
    try:
        is_private = True if os.environ.get('OMAHA_SERVER_PRIVATE', '').title() == 'True' else False

        if is_private:
            migrate()
            create_db_public_user()
            loaddata()
            create_admin()
            collectstatic()

        sh('/usr/bin/supervisord')
    except:
        client.captureException()
        raise


@task
def docker_run_test():
    sh('apt-get install -y python-dev libxslt-dev')
    sh('pip install -r requirements-test.txt --use-mirrors')
    test()


@task
def run_test_in_docker():
    sh('docker-compose -f docker-compose.dev.yml -p dev run --rm web paver docker_run_test')
