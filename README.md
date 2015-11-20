# omaha-server

[![Build Status](https://travis-ci.org/Crystalnix/omaha-server.svg?branch=master)](https://travis-ci.org/Crystalnix/omaha-server)
[![Coverage Status](https://coveralls.io/repos/Crystalnix/omaha-server/badge.png?branch=master)](https://coveralls.io/r/Crystalnix/omaha-server?branch=master)
[![Code Health](https://landscape.io/github/Crystalnix/omaha-server/master/landscape.svg?style=flat)](https://landscape.io/github/Crystalnix/omaha-server/master)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/Crystalnix/omaha-server/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/Crystalnix/omaha-server/?branch=master)
[![Apache License, Version 2.0](https://img.shields.io/badge/license-Apache%202.0-red.svg)](https://github.com/Crystalnix/omaha-server/blob/master/LICENSE)
[![](https://badge.imagelayers.io/crystalnix/omaha-server:master.svg)](https://imagelayers.io/?images=crystalnix/omaha-server:master 'Get your own badge on imagelayers.io')

Google Omaha server implementation + added Sparkle (mac) feed management

## Setting up a development server

**Requirements:**

- Ubuntu Trusty 14.04 (LTS) (64-bit)
- [paver](http://paver.github.io/paver/)
- [docker](docker.com) or [boot2docker](https://github.com/boot2docker/boot2docker) for OS X & Windows
- [docker-compose](https://docs.docker.com/compose/install/)

```shell
$ sudo apt-get update
$ sudo apt-get install docker.io
$ sudo apt-get install python-paver python-pip
$ sudo pip install -U docker-compose
$ git clone https://github.com/Crystalnix/omaha-server.git
$ cd omaha-server
$ sudo paver up_local_dev_server

# Stop server
$ sudo docker-compose stop
```

Open `http://{DOCKER_HOST}:9090/admin/`

- username: `admin`
- password: `admin`

## Setting up a development environment

**Requirements:**

- python 2.7
- [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/)
- PostgreSQL
- Redis

```shell
$ mkvirtualenv omaha-server
$ pip install -r requirements/dev.txt
```

### Tests

```shell
$ paver test
```

or

```shell
$ paver run_test_in_docker
```

## Statistics

Required `userid`. [Including user id into request](https://github.com/Crystalnix/omaha/wiki/Omaha-Client-working-with-protocol#including-user-id-into-request)

## Utils

A command for generating fake data such as requests, events and statistics:

```shell
# Usage: ./manage.py generate_fake_data [options] <app_id>
# Options:
#     --count=COUNT         Total number of data values (default: 100)
$ ./manage.py generate_fake_data {F07B3878-CD6F-4B96-B52F-95C4D2} --count=20
```

A command for generating fake statistics:

```shell
# Usage: ./manage.py generate_fake_statistics [options]
# Options:
#     --count=COUNT         Total number of data values (default: 100)
$ ./manage.py generate_fake_statistics --count=3000
```

## Deploying Omaha-Server to AWS Elastic Beanstalk

**Requirements:**

- [Elastic Beanstalk command line tools](http://aws.amazon.com/code/6752709412171743)
- [ebs-deploy](https://github.com/briandilley/ebs-deploy)
- [Sentry](https://github.com/getsentry/sentry)
    + [SetUp Sentry as self-hosted solution](http://sentry.readthedocs.org/en/latest/quickstart/index.html)
    + [Sentry as SaaS solution](https://www.getsentry.com/)
- AWS RDS: [Creating a DB Instance Running the PostgreSQL Database Engine](http://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_CreatePostgreSQLInstance.html)
- Redis instance in AWS ElasticCache: [Documentation](http://docs.aws.amazon.com/AmazonElastiCache/latest/UserGuide/GettingStarted.CreateCluster.Redis.html)
- AWS S3: [Create a Bucket](http://docs.aws.amazon.com/AmazonS3/latest/gsg/CreatingABucket.html)
- [AWS Access Key ID and Secret Access Key](http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html)

### Initializing the Configuration

```shell
$ cd deploy
$ cp settings.yml.example settings.yml
```

To change Omaha-Server configuration, add the settings that you want to modify to the `ebs.config` file. For example:

```yml
deploy:
  aws_access_key: '**********'
  aws_secret_key: '**********'
  bucket: 'example-ebs-archives'
  region: 'us-east-1' # http://docs.aws.amazon.com/general/latest/gr/rande.html#ec2_region

app:
  name: 'omaha-server'
  description: 'Omaha Server'

  key_name: 'omaha_server'

  solution_stack_name: '64bit Amazon Linux 2015.03 v1.4.3 running Docker 1.6.2' # optional default: '64bit Amazon Linux 2015.03 v1.4.3 running Docker 1.6.2'
  InstanceType: 't2.large' # optional default: t2.small http://aws.amazon.com/ec2/instance-types/
  autoscaling: # optional default: min=1 max=10
    min: 4
    max: 20
  healthcheck_url: '/admin/' # optional default: '/healthcheck/status/'

  environments:
    omaha-server-private:
      option_settings: # Configuration Options http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/command-options.html
        'aws:autoscaling:launchconfiguration':
          IamInstanceProfile: 'omaha-public'
          SecurityGroups: 'omaha-server,omaha-server-private' # If you use Amazon VPC with Elastic Beanstalk so that your instances are launched within a virtual private cloud (VPC), specify security group IDs instead of a security group name.

        'aws:ec2:vpc':
          VPCId: 'vpc-bb6b9fdf'
          Subnets: 'subnet-e386d5ba'
          AssociatePublicIpAddress: 'true'

      environment:
        OMAHA_SERVER_PRIVATE: 'true'
        SECRET_KEY: '**********'
        DB_HOST: 'postgres.example.com'
        DB_USER: 'omaha'
        DB_NAME: 'omaha'
        DB_PASSWORD: '**********'
        AWS_STORAGE_BUCKET_NAME: 'omaha-server'
        RAVEN_DNS: 'http://b3615b99118949dbae3c7d06e93fa74c:b8f1c35d08ef4bcaa6810b4d4cdd6fc0@sentry.example.com/2'
        RAVEN_DSN_STACKTRACE: 'http://637c17c832f44663b381916d4e0cb34d:9df83034cdfb400f9ce7d47ae4a0cc0b@sentry.example.com/5'
        REDIS_HOST: 'redis.example.com'
        DB_PUBLIC_USER: 'omaha_public'
        DB_PUBLIC_PASSWORD: 'omaha_public_password'
        AWS_ROLE: 'omaha-private'

    omaha-server-public:
      option_settings:
        'aws:autoscaling:launchconfiguration':
          IamInstanceProfile: 'omaha-public'
          SecurityGroups: 'omaha-server,omaha-server-public'
      environment:
        OMAHA_SERVER_PRIVATE: 'false'
        SECRET_KEY: '**********'
        DB_HOST: 'postgres.example.com'
        DB_USER: 'omaha_public'
        DB_NAME: 'omaha'
        DB_PASSWORD: 'omaha_public_password'
        AWS_STORAGE_BUCKET_NAME: 'omaha-server'
        RAVEN_DNS: 'http://b3615b99118949dbae3c7d06e93fa74c:b8f1c35d08ef4bcaa6810b4d4cdd6fc0@sentry.example.com/2'
        RAVEN_DSN_STACKTRACE: 'http://637c17c832f44663b381916d4e0cb34d:9df83034cdfb400f9ce7d47ae4a0cc0b@sentry.example.com/5'
        REDIS_HOST: 'redis.example.com'
        AWS_ROLE: 'omaha-public'
        DJANGO_SETTINGS_MODULE: 'omaha_server.settings_prod'
```

#### Environment variables

| Environment variable name |    Description    |       Default value        |
|---------------------------|-------------------|----------------------------|
| APP_VERSION               | App version       | DEV                        |
| DJANGO_SETTINGS_MODULE    |                   | omaha_server.settings_prod |
| SECRET_KEY                | Django SECRET_KEY |                            |
| HOST_NAME                 | Eb app host name  |                            |
| DB_HOST                   | DB Host           | 127.0.0.1                  |
| DB_USER                   | DB User           | postgres                   |
| DB_NAME                   | DB Name           | postgres                   |
| DB_PASSWORD               | DB Password       | ''                         |
| DB_PORT                   | DB port           | 5432                       |
| AWS_ACCESS_KEY_ID         | AWS Access Key    |                            |
| AWS_SECRET_ACCESS_KEY     | AWS Secret Key    |                            |
| AWS_STORAGE_BUCKET_NAME   | S3 storage bucket |                            |
| RAVEN_DNS                 | Sentry url        |                            |
| RAVEN_DSN_STACKTRACE      | Sentry url        | RAVEN_DNS                  |
| REDIS_HOST                | Redis host        | 127.0.0.1                  |
| REDIS_PORT                | Redis port        | 6379                       |
| REDIS_DB                  | Redis db          | 1                          |
| REDIS_STAT_PORT           | For statistics    | REDIS_PORT                 |
| REDIS_STAT_HOST           |                   | REDIS_HOST                 |
| REDIS_STAT_DB             |                   | 15                         |
| UWSGI_PROCESSES           |                   |                            |
| UWSGI_THREADS             |                   |                            |
| OMAHA_SERVER_PRIVATE      | Is private server | False                      |
| DB_PUBLIC_USER            |                   |                            |
| DB_PUBLIC_PASSWORD        |                   |                            |
| AWS_ROLE                  |                   |                            |
| OMAHA_URL_PREFIX          | no trailing slash!|                            |

- [uWSGI Options](http://uwsgi-docs.readthedocs.org/en/latest/Options.html) & [Environment variables](http://uwsgi-docs.readthedocs.org/en/latest/Configuration.html#environment-variables)
- [Sentry](https://github.com/getsentry/sentry)

### Initialize your ElasticBeanstalk application

```shell
# generate config file
$ python main.py
$ ebs-deploy init
```

### Deploy your application

```shell
$ ebs-deploy deploy -e omaha-server-dev
```

## Links

- Presentation: [omaha-server High Fidelity, High Velocity Deployments in the Cloud](http://slides.com/andreylisin/omaha-server/#/)

## Copyright and license

This software is licensed under the Apache 2 license, quoted below.

Copyright 2014 [Crystalnix Limited](http://crystalnix.com)

Licensed under the Apache License, Version 2.0 (the "License"); you may not
use this file except in compliance with the License. You may obtain a copy of
the License at

[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations under
the License.
