# omaha-server

[![Build Status](https://travis-ci.org/dentalwings/omaha-server.svg?branch=master)](https://travis-ci.org/dentalwings/omaha-server)
[![Coverage Status](https://coveralls.io/repos/dentalwings/omaha-server/badge.png?branch=master)](https://coveralls.io/r/dentalwings/omaha-server?branch=master)
[![Apache License, Version 2.0](https://img.shields.io/badge/license-Apache%202.0-red.svg)](https://github.com/dentalwings/omaha-server/blob/master/LICENSE)

Google Omaha server implementation and Sparkle (mac) feed management.

Currently, Crystalnix's implementation is integrated into the updating processes of several organizations for products that require sophisticated update logic and advanced usage statistics. Crystalnix provide additional support and further enhancement on a contract basis. For a case study and enquiries please refer to [Crystalnix website](https://www.crystalnix.com/case-study/google-omaha)

## Setting up a development server

**Requirements:**

- [docker](docker.com)
  or [docker-machine](https://docs.docker.com/machine/install-machine/)
  or [docker-for-windows](https://docs.docker.com/docker-for-windows/install/)
  or [docker-for-mac](https://docs.docker.com/docker-for-mac/install/)
- [docker-compose](https://docs.docker.com/compose/install/)

```shell
# docker install on ubuntu
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
sudo apt-get update
sudo apt-get install docker-ce

# checkout the code, assuming you're in your favorite source directory already
git clone git@github.com:dentalwings/omaha-server.git

# start dev environment
./startp.sh

# stop server
docker-compose stop

# destroy containers and db storage volume
docker-compose down -v

# rebuild web container (when python dependencies change)
docker-compose build
```

Open `http://{DOCKER_HOST}:8000/admin/`

- username: `admin`
- password: `admin`

## Statistics

All statistics are stored in Redis. In order not to lose all data, we recommend to set up the backing up process. The proposed solution uses ElastiCache which supports [automatic backups](https://aws.amazon.com/en/blogs/aws/backup-and-restore-elasticache-redis-nodes/).
In the case of a self-hosted solution do not forget to set up backups.

Required `userid`. [Including user id into request](https://github.com/Crystalnix/omaha/wiki/Omaha-Client-working-with-protocol#including-user-id-into-request)

## Utils

A command for generating fake data such as requests, events and statistics:

```shell
# Usage: ./manage.py generate_fake_data [options] <app_id>
# Options:
#     --count=COUNT         Total number of data values (default: 100)
docker-compose exec django python manage.py generate_fake_data {F07B3878-CD6F-4B96-B52F-95C4D2} --count=20
```

A command for generating fake statistics:

```shell
# Usage: ./manage.py generate_fake_statistics [options]
# Options:
#     --count=COUNT         Total number of data values (default: 100)
docker-compose exec django python manage.py generate_fake_statistics --count=3000
```

A command for generating fake live data:

```shell
# Usage: ./manage.py generate_fake_live_data <app_id>
#
docker-compose exec django python manage.py generate_fake_live_data {c00b6344-038f-4e51-bcb1-33ffdd812d81}
```

A command for generating fake live data for Mac:

```shell
# Usage: ./manage.py generate_fake_mac_live_data <app_name> <channel>
#
docker-compose exec django python manage.py generate_fake_mac_live_data Application alpha
```

## Deploying Omaha-Server to AWS Elastic Beanstalk

**Requirements:**
- [Setup a Route53 HostedZone](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/CreatingHostedZone.html)
- Launch this CloudFormation Template [![Launch Stack](assets/launch-stack.png)](https://console.aws.amazon.com/cloudformation/home#/stacks/new?stackName=omaha&templateURL=https%3A%2F%2Fs3.ca-central-1.amazonaws.com%2Fdentalwings-cloudformation-templates%2Fomaha-server%2Fcloudformation_omaha.yml)
- [Elastic Beanstalk command line tools](https://docs.aws.amazon.com/de_de/elasticbeanstalk/latest/dg/eb-cli3-install.html)

**Optional:**
- [Sentry](https://github.com/getsentry/sentry) for getting stacktraces of the omaha server django app itself [![Launch Stack](assets/launch-stack.png)](https://console.aws.amazon.com/cloudformation/home#/stacks/new?stackName=sentry&templateURL=https%3A%2F%2Fs3.ca-central-1.amazonaws.com%2Fdentalwings-cloudformation-templates%2Faws-cloudformation-sentry%2Fcloudformation_sentry.yml)

### Deploy your application

look up the following output of the cloudformation stack
* BeanstalkApplicationName
* PrivateEnvironment
* PublicEnvironment

```shell
cd omaha_server # where the manage.py is located
eb init --region {AWS::Region} {BeanstalkApplicationName}
eb deploy {PrivateEnvironment|PublicEnvironment}
```

#### Environment variables

| Environment variable name |    Description       |       Default value        |
|---------------------------|----------------------|----------------------------|
| APP_VERSION               | App version          | DEV                        |
| DJANGO_SETTINGS_MODULE    |                      | omaha_server.settings_prod |
| SECRET_KEY                | Django SECRET_KEY    |                            |
| HOST_NAME                 | Eb app host name     |                            |
| DB_HOST                   | DB Host              | 127.0.0.1                  |
| DB_USER                   | DB User              | postgres                   |
| DB_NAME                   | DB Name              | postgres                   |
| DB_PASSWORD               | DB Password          | ''                         |
| DB_PORT                   | DB port              | 5432                       |
| AWS_ACCESS_KEY_ID         | AWS Access Key       |                            |
| AWS_SECRET_ACCESS_KEY     | AWS Secret Key       |                            |
| AWS_STORAGE_BUCKET_NAME   | S3 storage bucket    |                            |
| RAVEN_DNS                 | Sentry url           |                            |
| RAVEN_DSN_STACKTRACE      | Sentry url           | RAVEN_DNS                  |
| REDIS_HOST                | Redis host           | 127.0.0.1                  |
| REDIS_PORT                | Redis port           | 6379                       |
| REDIS_DB                  | Redis db             | 1                          |
| REDIS_STAT_PORT           | For statistics       | REDIS_PORT                 |
| REDIS_STAT_HOST           |                      | REDIS_HOST                 |
| REDIS_STAT_DB             |                      | 15                         |
| UWSGI_PROCESSES           |                      |                            |
| UWSGI_THREADS             |                      |                            |
| OMAHA_SERVER_PRIVATE      | Is private server    | False                      |
| DB_PUBLIC_USER            |                      |                            |
| DB_PUBLIC_PASSWORD        |                      |                            |
| AWS_ROLE                  |                      |                            |
| OMAHA_URL_PREFIX          | no trailing slash!   |                            |
| SENTRY_STACKTRACE_API_KEY | Auth API token       |                            |
| OMAHA_ONLY_HTTPS          | HTTPS-only           | False                      |
| CUP_REQUEST_VALIDATION    |                      | False                      |
| CRASH_TRACKER             | Sentry, ELK          | Sentry                     |
| LOGSTASH_HOST             | Logstash host        |                            |
| LOGSTASH_PORT             | Logstash TCP port    |                            |
| FILEBEAT_HOST             | Filebeat host        | 127.0.0.1                  |
| FILEBEAT_PORT             | Filebeat UDP port    | 9021                       |
| ELK_HOST                  | Logstash host        | ''                         |
| ELK_PORT                  | Logstash TCP port    | ''                         |
| FILEBEAT_DESTINATION      | filebeat output type | ''                         |
| LOG_NGINX_TO_FILEBEAT     | Send logs to filebeat| 'True'                     |
| EMAIL_SENDER              | Verified SES email   | ''                         |
| EMAIL_RECIPIENTS          | Feedback recepients  | ''                         |

#### Enable Client Update Protocol v2

1. Use [Omaha eckeytool](https://github.com/google/omaha/tree/master/omaha/tools/eckeytool) to generate private.pem key and cup_ecdsa_pubkey.{KEYID}.h files.
2. Add cup_ecdsa_pubkey.{KEYID}.h to Omaha source directory /path/to/omaha/omaha/net/, set CupEcdsaRequestImpl::kCupProductionPublicKey in /path/to/omaha/omaha/net/cup_ecdsa_request.cc to new key and build Omaha client.
3. Add private.pem keyid and path to omaha CUP_PEM_KEYS dictionary in the [settings.py](https://github.com/Crystalnix/omaha-server/blob/master/omaha_server/omaha_server/settings.py). If you run the server on AWS, create a `cups_pem_keys` folder in the S3 Bucket (AWS_STORAGE_BUCKET_NAME) and put the keys with the index as filename (e.g.: `1.pem`) in there.

## Contributors

Thanks to [Abiral Shrestha](https://twitter.com/proabiral) for the security reports and suggestions.

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
