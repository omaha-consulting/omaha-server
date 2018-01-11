FROM ubuntu-debootstrap:14.04

ENV omaha /srv/omaha

RUN \
  apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys ABF5BD827BD9BF62 && \
  echo 'deb http://nginx.org/packages/ubuntu/ trusty nginx' | tee --append /etc/apt/sources.list && \
  apt-get update && \
  apt-get install -y --no-install-recommends python-pip python-dev python-lxml python-psycopg2 supervisor nginx liblua5.1-dev lua-zlib libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev python-pil build-essential libfuse-dev libcurl4-openssl-dev libxml2-dev mime-support automake libtool pkg-config libssl-dev wget tar && \
  apt-get clean && \
  apt-get autoremove -y && \
  rm -rf /var/lib/{apt,dpkg,cache,log}/  && \
  pip install uwsgi

RUN \
  apt-get install -y --fix-missing curl && \
  curl -L -O https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-6.0.0-amd64.deb && \
  dpkg -i filebeat-6.0.0-amd64.deb && \
  mkdir /tmp/filebeat/

RUN mkdir -p $omaha/requirements
WORKDIR ${omaha}

ADD ./requirements/base.txt $omaha/requirements/base.txt

RUN \
  pip install paver && \
  pip install --upgrade six && \
  pip install -r requirements/base.txt

# build lua module for nginx
RUN \
  cd /tmp && \
  NGINX_VERSION=`nginx -v 2>&1 | grep -o '[[:digit:]].*$'` && \
  wget http://nginx.org/download/nginx-$NGINX_VERSION.tar.gz && \
  tar -xzvf nginx-$NGINX_VERSION.tar.gz && \
  wget -qO- https://api.github.com/repos/openresty/lua-nginx-module/tags | grep -m 1 tarball_url | cut -d '"' -f 4 | xargs wget -O lua-nginx-module.tar && \
  mkdir -p /tmp/lua-nginx-module && tar -xvf lua-nginx-module.tar -C /tmp/lua-nginx-module --strip-components=1 && \
  wget -qO- https://api.github.com/repos/simpl/ngx_devel_kit/tags | grep -m 1 tarball_url | cut -d '"' -f 4 | xargs wget -O ngx_devel_kit.tar && \
  mkdir -p /tmp/ngx_devel_kit && tar -xvf ngx_devel_kit.tar -C /tmp/ngx_devel_kit --strip-components=1 && \
  cd nginx-$NGINX_VERSION && \
  nginx -V 2>&1 | grep 'configure arguments: ' | cut -d ":" -f2 | xargs ./configure --add-dynamic-module=/tmp/ngx_devel_kit --add-dynamic-module=/tmp/lua-nginx-module && \
  make build && \
  cp objs/ndk_http_module.so /usr/lib/nginx/modules/ndk_http_module.so && \
  cp objs/ngx_http_lua_module.so /usr/lib/nginx/modules/ngx_http_lua_module.so && \
  cd /tmp && \
  rm -R /tmp/*

ENV AWS_STORAGE_BUCKET_NAME="" AWS_ROLE=""
