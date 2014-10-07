FROM ubuntu:14.04

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y python-pip python-lxml python-psycopg2 uwsgi supervisor
RUN apt-get install -y uwsgi-plugin-python
RUN apt-get clean

ADD . /srv/omaha
COPY ./conf/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

WORKDIR /srv/omaha


RUN pip install -r requirements.txt

RUN ./omaha_server/manage.py collectstatic --noinput
