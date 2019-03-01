.PHONY: build-base-old
build-base-old:
	docker build -t crystalnix/omaha-server-base:alpine -f Dockerfile-base-old .

.PHONY: build-base-alpine
build-base-alpine:
	docker build -t crystalnix/omaha-server-base:alpine -f Dockerfile-base-alpine .

.PHONY: build-dev
build-dev:
	docker build -t crystalnix/omaha-server:dev .

.PHONY: run-sh
run-sh:
	docker run -ti crystalnix/omaha-server:dev sh
