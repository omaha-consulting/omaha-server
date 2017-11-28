#!/bin/sh
# Sets up a omaha-server dev environment.
# Runs on a clean Ubuntu Server 14.04 LTS system.
# Runs unit tests to verify success.

set -x # Echo on

sudo apt-get update

# Install docker, paver, and virtualenv.
sudo apt-get -y install docker.io
sudo apt-get -y install python-paver python-pip python-virtualenv
sudo pip install -U docker-compose
sudo usermod -aG docker $USER

# Install postgres, redis, libraries.
sudo apt-get -y install postgresql postgresql-contrib
sudo apt-get -y install build-essential redis-server
sudo apt-get -y install libpq-dev python-dev libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev libffi-dev
sudo apt-get -y install libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk

# Create a virtual environment and install requirements there.
virtualenv venv
venv/bin/pip install -r requirements/dev.txt

# Run unit tests.
. venv/bin/activate
paver test