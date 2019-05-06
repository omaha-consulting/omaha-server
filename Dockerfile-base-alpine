FROM python:3.7-alpine3.9

ENV OMAHA_SERVER_PATH /srv/omaha
WORKDIR ${OMAHA_SERVER_PATH}

# Add low-level dependencies
RUN \
  apk add bash ca-certificates \
  && apk add nginx supervisor openrc \
  && apk add --virtual dev-deps build-base \
  && apk add py3-lxml py-psycopg2 py-pillow \
  && apk add fuse-dev libxml2-dev libxslt-dev libcurl curl-dev libstdc++ \
  && apk add --virtual fuse-deps autoconf automake libtool pkgconfig openssl-dev wget tar \
  && apk add linux-headers pcre-dev gd-dev geoip-dev \
  && apk add openssl pcre zlib zlib-dev \
  && apk add build-base lua5.1-dev luarocks \
  && apk add --no-cache postgresql-libs postgresql-dev libc6-compat gzip \
  && apk add --no-cache libffi-dev \
  && pip install lxml

# Prepare for building Nginx. Intsall LuaJIT.
RUN \
  apk add luajit luajit-dev nginx-lua nginx-mod-http-lua \
  && wget http://luajit.org/download/LuaJIT-2.1.0-beta3.tar.gz \
  && tar -xzvf LuaJIT-2.1.0-beta3.tar.gz && rm LuaJIT-2.1.0-beta3.tar.gz \
  && cd LuaJIT-2.1.0-beta3 \
  && make \
  && make install

ENV LUAJIT_LIB /usr/local/lib
ENV LUAJIT_INC /usr/local/include/luajit-2.1

# Build Lua module for Nginx
RUN \
  luarocks-5.1 install lua-zlib && \
  cd /tmp && \
  NGINX_VERSION=`nginx -v 2>&1 | grep -o '[[:digit:]].*$'` && \
  wget http://nginx.org/download/nginx-$NGINX_VERSION.tar.gz && \
  tar -xzvf nginx-$NGINX_VERSION.tar.gz && \
  wget -qO- https://api.github.com/repos/openresty/lua-nginx-module/tags | grep -m 1 tarball_url | cut -d '"' -f 4 | xargs wget -O lua-nginx-module.tar && \
  mkdir -p /tmp/lua-nginx-module && tar -xvf lua-nginx-module.tar -C /tmp/lua-nginx-module --strip-components=1 && \
  wget -qO- https://api.github.com/repos/simpl/ngx_devel_kit/tags | grep -m 1 tarball_url | cut -d '"' -f 4 | xargs wget -O ngx_devel_kit.tar && \
  mkdir -p /tmp/ngx_devel_kit && tar -xvf ngx_devel_kit.tar -C /tmp/ngx_devel_kit --strip-components=1 && \
  cd nginx-$NGINX_VERSION && \
  ./configure \
    --prefix=/var/lib/nginx \
    --sbin-path=/usr/sbin/nginx \
    --modules-path=/usr/lib/nginx/modules \
    --conf-path=/etc/nginx/nginx.conf \
    --pid-path=/run/nginx/nginx.pid \
    --lock-path=/run/nginx/nginx.lock \
    --http-client-body-temp-path=/var/tmp/nginx/client_body \
    --http-proxy-temp-path=/var/tmp/nginx/proxy \
    --http-fastcgi-temp-path=/var/tmp/nginx/fastcgi \
    --http-uwsgi-temp-path=/var/tmp/nginx/uwsgi \
    --http-scgi-temp-path=/var/tmp/nginx/scgi \
    --user=nginx \
    --group=nginx \
    --with-threads \
    --with-file-aio \
    --with-http_ssl_module \
    --with-http_v2_module \
    --with-http_realip_module \
    --with-http_addition_module \
    --with-http_xslt_module=dynamic \
    --with-http_image_filter_module=dynamic \
    --with-http_geoip_module=dynamic \
    --with-http_sub_module \
    --with-http_dav_module \
    --with-http_flv_module \
    --with-http_mp4_module \
    --with-http_gunzip_module \
    --with-http_gzip_static_module \
    --with-http_auth_request_module \
    --with-http_random_index_module \
    --with-http_secure_link_module \
    --with-http_degradation_module \
    --with-http_slice_module \
    --with-http_stub_status_module \
    --with-mail=dynamic \
    --with-mail_ssl_module \
    --with-stream=dynamic \
    --with-stream_ssl_module \
    --with-stream_realip_module \
    --with-stream_geoip_module=dynamic \
    --with-stream_ssl_preread_module \
    --add-dynamic-module=/tmp/ngx_devel_kit \
    --add-dynamic-module=/tmp/lua-nginx-module && \
  make build && \
  cp objs/ndk_http_module.so /usr/lib/nginx/modules/ndk_http_module.so && \
  cp objs/ngx_http_lua_module.so /usr/lib/nginx/modules/ngx_http_lua_module.so && \
  cd /tmp && \
  rm -R /tmp/*

# S3FS
ARG S3FS_VERSION=1.84
RUN \
  mkdir /usr/src/omaha-server \
  && wget --no-check-certificate https://github.com/s3fs-fuse/s3fs-fuse/archive/v${S3FS_VERSION}.tar.gz -O /usr/src/omaha-server/v${S3FS_VERSION}.tar.gz \
  && tar xvz -C /usr/src/omaha-server -f /usr/src/omaha-server/v${S3FS_VERSION}.tar.gz \
  && cd /usr/src/omaha-server/s3fs-fuse-${S3FS_VERSION} \
  && ./autogen.sh \
  && ./configure --prefix=/usr \
  && make \
  && make install \
  && mkdir -p /srv/omaha_s3 \
  && rm /usr/src/omaha-server/v${S3FS_VERSION}.tar.gz

# Filebeat
ARG FILEBEAT_PACKEGE=filebeat-6.0.0-linux-x86_64
RUN \
  wget https://artifacts.elastic.co/downloads/beats/filebeat/${FILEBEAT_PACKEGE}.tar.gz -O /usr/src/omaha-server/${FILEBEAT_PACKEGE}.tar.gz \
  && tar xzvf /usr/src/omaha-server/${FILEBEAT_PACKEGE}.tar.gz -C /etc/ \
  && mv /etc/${FILEBEAT_PACKEGE} /etc/filebeat \
  && mkdir /tmp/filebeat/ \
  && ln /etc/filebeat/filebeat /usr/bin/


# Clean Up
RUN \
  rm -rf /var/cache/apk/* \
  && apk del fuse-deps dev-deps

# Setup application dependencies
RUN mkdir -p $OMAHA_SERVER_PATH/requirements
ADD Pipfile Pipfile.lock $OMAHA_SERVER_PATH/

# Dependencies for Pillow
RUN apk add jpeg-dev libjpeg \
  && apk add rsyslog

RUN \
  pip install pipenv \
  && pipenv install --system --deploy
