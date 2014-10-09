# coding: utf8

from paver.easy import task
from paver.easy import sh


@task
def test():
    sh('./manage.py test', cwd='omaha_server')


@task
def up_dev_server():
    """
    Requirements:

    - [docker](docker.com) or [boot2docker](https://github.com/boot2docker/boot2docker) for OS X or Windows
    - [fig](fig.sh)

    """
    sh('fig up -d')
    sh('fig stop web')
    sh('fig start web')
    sh('fig run web ./manage.py migrate')
    sh('fig run web ./manage.py createsuperuser --username=admin --email=admin@example.com --noinput')
    sh('fig run web ./manage.py set_fake_passwords --password=admin')
    print """Open http://DOCKER_HOST:9090/admin/\n username: admin\n password: admin"""
