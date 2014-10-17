# omaha-server

[![Build Status](https://travis-ci.org/Crystalnix/omaha-server.svg?branch=master)](https://travis-ci.org/Crystalnix/omaha-server)
[![Coverage Status](https://coveralls.io/repos/Crystalnix/omaha-server/badge.png?branch=master)](https://coveralls.io/r/Crystalnix/omaha-server?branch=master)

Google Omaha server implementation + added Sparkle (mac) feed management

© 2014 [Crystalnix](http://crystalnix.com) [contacts@crystalnix.com](mailto:contacts@crystalnix.com)

## Setting up a development server

**Requirements:**

- [paver](http://paver.github.io/paver/)
- [docker](docker.com) or [boot2docker](https://github.com/boot2docker/boot2docker) for OS X & Windows
- [fig](fig.sh)

```sh
$ paver up_local_dev_server
```

Open http://{DOCKER_HOST}:9090/admin/

- username: `admin`
- password: `admin`

## Setting up a development environment

**Requirements:**

- python 2.7
- [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/)
- PostgreSQL
- Redis

```sh
$ mkvirtualenv omaha-server
$ pip install -r requirements-dev.txt
```

## Tests

```sh
$ paver test
```

or

```sh
$ paver run_test_in_docker
```

## Deploying a Omaha-Server to AWS Elastic Beanstalk

**Requirements:**

- [Elastic Beanstalk command line tools](http://aws.amazon.com/code/6752709412171743)
- [ebs-deploy](https://github.com/briandilley/ebs-deploy)

### Initialize your application

```sh
$ cd omaha_server
$ cp cp ebs.config.example ebs.config
$ ebs-deploy init
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
| REDIS_HOST                | Redis host        | 127.0.0.1                  |
| REDIS_PORT                | Redis port        | 6379                       |
| REDIS_DB                  | Redis db          | 1                          |




### Deploy your application

```sh
$ ebs-deploy deploy -e omaha-server-dev
```
