FROM ubuntu:14.04

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y python-pip python-lxml python-psycopg2 uwsgi supervisor
RUN apt-get install -y uwsgi-plugin-python
RUN apt-get install -y nginx
RUN apt-get clean

ADD . /srv/omaha

# setup all the configfiles
RUN rm /etc/nginx/sites-enabled/default
RUN rm /etc/nginx/nginx.conf
RUN ln -s /srv/omaha/conf/nginx.conf /etc/nginx/
RUN ln -s /srv/omaha/conf/nginx-app.conf /etc/nginx/sites-enabled/
RUN ln -s /srv/omaha/conf/supervisord.conf /etc/supervisor/conf.d/

WORKDIR /srv/omaha

RUN pip install paver --use-mirrors
RUN pip install -r requirements.txt --use-mirrors

EXPOSE 80
ENTRYPOINT ["paver", "docker_run"]