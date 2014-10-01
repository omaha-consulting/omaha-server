# omaha-server

[![Build Status](https://travis-ci.org/Crystalnix/omaha-server.svg?branch=python-omaha)](https://travis-ci.org/Crystalnix/omaha-server)
[![Coverage Status](https://coveralls.io/repos/Crystalnix/omaha-server/badge.png?branch=python-omaha)](https://coveralls.io/r/Crystalnix/omaha-server?branch=python-omaha)

## Setting up a development server

**Requirements:**

- [docker](docker.com) or [boot2docker](https://github.com/boot2docker/boot2docker) for OS X or Windows
- [fig](fig.sh)
- [paver](http://paver.github.io/paver/)

```sh
$ paver up_dev_server
```

## Setting up a development environment

**Requirements:**

- python 2.7 
- [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/)
- PostgreSQL

```sh
$ mkvirtualenv omaha-server
$ pip install -r requirements-dev.txt
```

## Tests

```sh
$ paver test
```
