FROM art2ihs/omaha-server:0000

ENV omaha /srv/omaha

RUN mkdir -p $omaha/requirements
WORKDIR ${omaha}

ADD . $omaha

EXPOSE 80
CMD ["paver", "docker_run"]
