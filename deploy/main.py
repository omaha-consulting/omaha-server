#!/usr/bin/env python
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

import yaml
from jinja2 import Template

BASE_DIR = os.path.dirname(__file__)
TEMPLATE_PATH = os.path.join(BASE_DIR, 'ebs.config.template')
CONFIG_SAVE_PATH = os.path.join(BASE_DIR, 'ebs.config')
SETTINGS_PATH = os.path.join(BASE_DIR, 'settings.yml')
DEFAULT_SETTINGS = dict(
    app=dict(
        versions_to_keep=10,
        solution_stack_name='64bit Amazon Linux 2016.03 v2.1.0 running Docker 1.9.1',
        InstanceType='t2.small',
        autoscaling=dict(min=1, max=10),
        healthcheck_url='/healthcheck/status/',
    ),
    environment=dict(
        DJANGO_SETTINGS_MODULE='omaha_server.settings_dev',
        UWSGI_PROCESSES=10,
        UWSGI_THREADS=8,
    ),
)


def get_settings():
    with open(SETTINGS_PATH, 'r') as f:
        settings = yaml.load(f)

    app_settings = DEFAULT_SETTINGS['app'].copy()
    app_settings.update(settings['app'])
    settings['app'] = app_settings

    environments = settings['app']['environments']
    for env in environments.keys():
        environment = DEFAULT_SETTINGS['environment'].copy()
        environment.update(environments[env]['environment'])
        environments[env]['environment'] = environment

    return settings


def get_template():
    with open(TEMPLATE_PATH, 'r') as f:
        text = f.read()
    return Template(text)


def save_config(data):
    with open(CONFIG_SAVE_PATH, 'w') as f:
        f.write(data)


def main():
    template = get_template()
    ebs_config = template.render(**get_settings())
    save_config(ebs_config)


if __name__ == '__main__':
    main()
