from django_nose.runner import NoseTestSuiteRunner
from django.db import connections
from copy import copy

class PublicPrivateNoseTestSuiteRunner(NoseTestSuiteRunner):
    def setup_databases(self):
        res = super(PublicPrivateNoseTestSuiteRunner, self).setup_databases()
        connections.databases['root'] = copy(connections.databases['default'])
        connections.close_all()
        return res