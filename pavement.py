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
    sh('./manage.py migrate --noinput', cwd='omaha_server')


@task
def create_admin():
    sh('./createadmin.py', cwd='omaha_server')


@task
def configure_nginx():
    filebeat_host = os.environ.get('FILEBEAT_HOST', '')
    filebeat_port = os.environ.get('FILEBEAT_PORT', '')
    log_nginx_to_filebeat = True if os.environ.get('LOG_NGINX_TO_FILEBEAT', 'True').title() == 'True' else False
    if log_nginx_to_filebeat and filebeat_host and filebeat_port.isdigit():
        sh("sed -i 's/access_log.*;/access_log syslog:server=%s:%s main;/g' /etc/nginx/nginx.conf" % (filebeat_host, filebeat_port))
        sh("sed -i 's/error_log.*;/error_log syslog:server=%s:%s;/g' /etc/nginx/nginx.conf" % (filebeat_host, filebeat_port))
    else:
        sh("sed -i 's#access_log.*;#access_log /var/log/nginx/access.log main;#g' /etc/nginx/nginx.conf")
        sh("sed -i 's#error_log.*;#error_log /var/log/nginx/error.log;#g' /etc/nginx/nginx.conf")
    server_name = os.environ.get('HOST_NAME', '_')
    server_name = server_name if server_name != '*' else '_'
    sh("sed -i 's/server_name.*;/server_name %s;/g' /etc/nginx/sites-enabled/nginx-app.conf" % (server_name))


def elasticsearch_output(elasticsearch_host, elasticsearch_port):
    sh("sed -i 's/hosts: \[\"localhost:9200\"]/hosts: \[\"%s:%s\"]/g' /etc/filebeat/filebeat.yml" % (elasticsearch_host, elasticsearch_port))


def logstash_output(logstash_host, logstash_port):
    elasticsearch_output_disabled()
    sh("sed -i 's/#output.logstash:/output.logstash:/g' /etc/filebeat/filebeat.yml")
    sh("sed -i 's/#hosts: \[\"localhost:5044\"]/hosts: \[\"%s:%s\"]/g' /etc/filebeat/filebeat.yml" % (logstash_host, logstash_port))


def filename_output():
    elasticsearch_output_disabled()
    sh("sed -i 's/#output.file:/output.file:/g' /etc/filebeat/filebeat.yml")
    sh("sed -i 's@#path: \"/tmp/filebeat\"@path: \"/tmp/filebeat\"@g' /etc/filebeat/filebeat.yml")
    sh("sed -i 's/#filename: filebeat/filename: filebeat/g' /etc/filebeat/filebeat.yml")


def elasticsearch_output_disabled():
    sh("sed -i 's/setup.template.enabled: true/setup.template.enabled: false/g' /etc/filebeat/filebeat.yml")
    sh("sed -i 's/output.elasticsearch:/#output.elasticsearch:/g' /etc/filebeat/filebeat.yml")
    sh("sed -i 's/hosts: \[\"localhost:9200\"]/#hosts: \[\"localhost:9200\"]/g' /etc/filebeat/filebeat.yml")


@task
def configure_filebeat():
    elk_host = os.environ.get('ELK_HOST', '')
    elk_port = os.environ.get('ELK_PORT', '')
    filebeat_destination = os.environ.get('FILEBEAT_DESTINATION', '')
    filebeat_destination = filebeat_destination.lower()
    if filebeat_destination == 'elasticsearch' and elk_host and elk_port.isdigit():
        configure_elasticsearch(elk_host, elk_port)
        elasticsearch_output(elk_host, elk_port)
    elif filebeat_destination == 'logstash' and elk_host and elk_port.isdigit():
        logstash_output(elk_host, elk_port)
    else:
        filename_output()

def configure_elasticsearch(elk_host, elk_port):
   filter_path = os.path.abspath("conf/standard_filter.json")
   sh("curl -XPUT '%s:%s/_ingest/pipeline/standard_filter?pretty' -H 'Content-Type: application/json' -d @%s" % (elk_host, elk_port, filter_path))


@task
def docker_run():
    try:
        is_private = True if os.environ.get('OMAHA_SERVER_PRIVATE', '').title() == 'True' else False

        if is_private:
            migrate()
            loaddata()
            create_admin()
            collectstatic()
        configure_nginx()
        configure_filebeat()
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
        sh('docker-compose -f docker-compose.tests.yml -p omaha_testing run --rm sut paver docker_run_test')
    except:
        pass
    sh('docker-compose -f docker-compose.tests.yml -p omaha_testing stop')
    sh('docker-compose -f docker-compose.tests.yml -p omaha_testing rm --force')
