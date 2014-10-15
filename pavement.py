# coding: utf8

from paver.easy import task
from paver.easy import sh


@task
def test():
    sh('./manage.py test', cwd='omaha_server')


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
