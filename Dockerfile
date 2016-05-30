FROM ubuntu-debootstrap:14.04

ENV omaha /srv/omaha
ENV LUAJIT_LIB /usr/local/lib
ENV LUAJIT_INC /usr/local/include/luajit-2.0

RUN \
  apt-get update && \
  apt-get install build-essential wget make libpcre3 libpcre3-dev openssl libssl-dev libperl-dev libxslt-dev libgd2-xpm-dev libgeoip-dev -y && \
  cd /tmp && \
  wget http://luajit.org/download/LuaJIT-2.0.4.tar.gz && wget https://github.com/simpl/ngx_devel_kit/archive/v0.3.0.tar.gz && wget https://github.com/openresty/lua-nginx-module/archive/v0.10.4.tar.gz && wget http://nginx.org/download/nginx-1.10.0.tar.gz && \
  ls *.tar.gz | xargs -i tar xzf {} && \
  (cd LuaJIT-2.0.4 && make && make install) && \
  export LUAJIT_LIB=/usr/local/lib LUAJIT_INC=/usr/local/include/luajit-2.0 && \
  (cd nginx-1.10.0 && ./configure --prefix=/etc/nginx --sbin-path=/usr/sbin/nginx --modules-path=/usr/lib/nginx/modules --conf-path=/etc/nginx/nginx.conf --error-log-path=/var/log/nginx/error.log --http-log-path=/var/log/nginx/access.log --pid-path=/var/run/nginx.pid --lock-path=/var/run/nginx.lock --http-client-body-temp-path=/var/cache/nginx/client_temp --http-proxy-temp-path=/var/cache/nginx/proxy_temp --http-fastcgi-temp-path=/var/cache/nginx/fastcgi_temp --http-uwsgi-temp-path=/var/cache/nginx/uwsgi_temp --http-scgi-temp-path=/var/cache/nginx/scgi_temp --user=nginx --group=nginx --with-http_ssl_module --with-http_realip_module --with-http_addition_module --with-http_sub_module --with-http_dav_module --with-http_flv_module --with-http_mp4_module --with-http_gunzip_module --with-http_gzip_static_module --with-http_random_index_module --with-http_secure_link_module --with-http_stub_status_module --with-http_auth_request_module --with-http_xslt_module=dynamic --with-http_image_filter_module=dynamic --with-http_geoip_module=dynamic --with-http_perl_module=dynamic --with-threads --with-stream --with-stream_ssl_module --with-http_slice_module --with-mail --with-mail_ssl_module --with-file-aio --with-ipv6 --with-http_v2_module --with-cc-opt='-g -O2 -fstack-protector --param=ssp-buffer-size=4 -Wformat -Werror=format-security -Wp,-D_FORTIFY_SOURCE=2' --with-ld-opt='-Wl,-Bsymbolic-functions -Wl,-z,relro -Wl,--as-needed' --add-module=/tmp/ngx_devel_kit-0.3.0 --add-module=/tmp/lua-nginx-module-0.10.4 && make && make install) && \
  ldconfig && \
  mkdir /var/cache/nginx && \
  rm -rf /tmp/*

RUN \
  apt-get install -y --no-install-recommends python-pip python-dev python-lxml python-psycopg2 supervisor libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev python-pil build-essential libfuse-dev libcurl4-openssl-dev libxml2-dev mime-support automake libtool pkg-config libssl-dev wget tar && \
  apt-get clean && \
  apt-get autoremove -y && \
  rm -rf /var/lib/{apt,dpkg,cache,log}/  && \
  pip install uwsgi

RUN \
  wget https://github.com/s3fs-fuse/s3fs-fuse/archive/v1.78.tar.gz -O /usr/src/v1.78.tar.gz && \
  tar xvz -C /usr/src -f /usr/src/v1.78.tar.gz && \
  cd /usr/src/s3fs-fuse-1.78 && \
  ./autogen.sh && \
  ./configure --prefix=/usr && \
  make && \
  make install && \
  mkdir /srv/omaha_s3 && \
  rm /usr/src/v1.78.tar.gz


RUN mkdir -p $omaha/requirements
WORKDIR ${omaha}

ADD ./requirements/base.txt $omaha/requirements/base.txt

RUN \
  pip install paver && \
  pip install --upgrade six && \
  pip install -r requirements/base.txt

ADD . $omaha

# setup all the configfiles
RUN \
  mkdir /etc/nginx/sites-enabled/ && \
#  rm /etc/nginx/conf.d/default.conf && \
  rm /etc/nginx/nginx.conf && \
  ln -s /srv/omaha/conf/nginx.conf /etc/nginx/ && \
  ln -s /srv/omaha/conf/nginx-app.conf /etc/nginx/sites-enabled/ && \
  ln -s /srv/omaha/conf/supervisord.conf /etc/supervisor/conf.d/

EXPOSE 80
CMD ["paver", "docker_run"]
