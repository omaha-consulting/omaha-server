# coding: utf8

from paver.easy import task
from paver.easy import sh


@task
def test():
    sh('nosetests')
