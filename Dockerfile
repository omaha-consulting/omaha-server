FROM ubuntu:14.04.1

ENV omaha /srv/omaha

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y python-pip python-lxml python-psycopg2 uwsgi supervisor
RUN apt-get install -y uwsgi-plugin-python
RUN apt-get install -y nginx
RUN apt-get install -y libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev python-pil


# install s3fs

RUN apt-get install -y build-essential
RUN apt-get install -y libfuse-dev
RUN apt-get install -y libcurl4-openssl-dev
RUN apt-get install -y libxml2-dev
RUN apt-get install -y mime-support
RUN apt-get install -y automake
RUN apt-get install -y libtool
RUN apt-get install -y pkg-config
RUN apt-get install -y libssl-dev
RUN apt-get install -y wget tar
RUN apt-get clean

RUN wget https://github.com/s3fs-fuse/s3fs-fuse/archive/v1.78.tar.gz -O /usr/src/v1.78.tar.gz
RUN tar xvz -C /usr/src -f /usr/src/v1.78.tar.gz
RUN cd /usr/src/s3fs-fuse-1.78 && ./autogen.sh && ./configure --prefix=/usr && make && make install
RUN mkdir /srv/omaha_s3


ADD . $omaha

# setup all the configfiles
RUN rm /etc/nginx/sites-enabled/default
RUN rm /etc/nginx/nginx.conf
RUN ln -s /srv/omaha/conf/nginx.conf /etc/nginx/
RUN ln -s /srv/omaha/conf/nginx-app.conf /etc/nginx/sites-enabled/
RUN ln -s /srv/omaha/conf/supervisord.conf /etc/supervisor/conf.d/

WORKDIR ${omaha}

RUN pip install paver --use-mirrors
RUN pip install -r requirements.txt --use-mirrors

EXPOSE 80
CMD ["paver", "docker_run"]
