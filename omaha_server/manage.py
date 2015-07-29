#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    settings = "omaha_server.settings_test" if 'test' in sys.argv else 'omaha_server.settings'
    if 'test' in sys.argv:
        os.environ['OMAHA_SERVER_PRIVATE'] = 'True'
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
