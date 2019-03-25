FROM crystalnix/omaha-server-base:alpine

# Install Dev and Test requirements
RUN pipenv install --system --dev

ADD . $omaha

# Setup all the configfiles
RUN \
  mkdir /etc/nginx/sites-enabled/ && \
  rm /etc/filebeat/filebeat.yml && \
  rm /etc/nginx/conf.d/default.conf && \
  rm /etc/nginx/nginx.conf && \
  rm /etc/supervisord.conf && \
  ln -s /srv/omaha/conf/nginx.conf /etc/nginx/ && \
  ln -s /srv/omaha/conf/nginx-app.conf /etc/nginx/sites-enabled/ && \
  ln -s /srv/omaha/conf/inflate_request.lua /var/lib/nginx && \
  ln -s /srv/omaha/conf/supervisord.conf /etc/ && \
  ln -s /srv/omaha/conf/filebeat.yml /etc/filebeat/ && \
  chmod go-w /etc/filebeat/filebeat.yml

EXPOSE 80
EXPOSE 8080
CMD ["paver", "docker_run"]
