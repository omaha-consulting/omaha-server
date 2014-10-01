FROM ubuntu:14.04

RUN apt-get update
RUN apt-get upgrade -y
#RUN apt-get install -y python-pip libpq-dev python-dev libxml2-dev libxslt1-dev
RUN apt-get install -y python-pip python-lxml python-psycopg2
RUN apt-get clean

ADD . /srv/omaha

WORKDIR /srv/omaha

RUN pip install -r requirements.txt
