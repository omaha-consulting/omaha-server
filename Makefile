DOCKER_REGISTRY_BASE=crystalnix/omaha-server-base
DOCKER_REGISTRY=crystalnix/omaha-server
BASE_IMAGE_TAG=alpine
DEVELOP_IMAGE_TAG=develop
STABLE_IMAGE_TAG=stable
DOCKER_COMPOSE=docker-compose -f docker-compose.dev.yml -p dev

.PHONY: build-dev-web
build-dev-web:
	$(DOCKER_COMPOSE) build web

.PHONY: build-base
build-base:
	docker build -t $(DOCKER_REGISTRY_BASE):$(BASE_IMAGE_TAG) -f Dockerfile-base-alpine .

.PHONY: build-dev
build-dev:
	docker build -t $(DOCKER_REGISTRY):$(DEVELOP_IMAGE_TAG) -f Dockerfile-dev .

.PHONY: build-stable
build-stable:
	docker build -t $(DOCKER_REGISTRY):$(STABLE_IMAGE_TAG) .

.PHONY: install-dev
install-dev:
	pipenv install --dev

.PHONY: lock
lock:
	pipenv lock

.PHONY: virtual-env
virtual-env:
	pipenv shell

.PHONY: test
test:
	pipenv run paver run_test_in_docker

.PHONY: test-without-docker
test-without-docker:
	pipenv run paver test

.PHONY: up
up: build-dev-web
	pipenv run paver up_local_dev_server

.PHONY: exec
exec:
	$(DOCKER_COMPOSE) exec web sh

.PHONY: ps
ps:
	$(DOCKER_COMPOSE) ps

.PHONY: logs
logs:
	$(DOCKER_COMPOSE) logs -f web

.PHONY: stop
stop:
	$(DOCKER_COMPOSE) stop

.PHONY: rm
rm:
	$(DOCKER_COMPOSE) rm -f

.PHONY: push-base-image
push-base-image: build-base
	docker push $(DOCKER_REGISTRY_BASE):$(BASE_IMAGE_TAG)

.PHONY: push-dev-image
push-dev-image: build-dev
	docker push $(DOCKER_REGISTRY):$(DEVELOP_IMAGE_TAG)

.PHONY: push-stable-image
push-stable-image: build-stable
	docker push $(DOCKER_REGISTRY):$(STABLE_IMAGE_TAG)
