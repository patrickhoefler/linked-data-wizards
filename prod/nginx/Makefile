default: build

.PHONY: build
build:
	# Build patrickhoefler/linked-data-wizards
	docker build --tag=patrickhoefler/linked-data-wizards ../..

	# Run patrickhoefler/linked-data-wizards as ldw-static-files
	docker run \
	  --name=ldw-static-files \
	  -e STATIC_ROOT=/static \
	  -e LDW_VIRTUOSO_PORT_8890_TCP_ADDR='' \
	  -e LDW_VIRTUOSO_PORT_8890_TCP_PORT='' \
	  -e SECRET_KEY='' \
	  -d \
	  patrickhoefler/linked-data-wizards \
	  sleep 999

	# Collect the static files
	docker exec ldw-static-files mkdir /static
	docker exec ldw-static-files python manage.py collectstatic --noinput > /dev/null

	# Copy static files to build directory
	docker cp ldw-static-files:/static .

	# Stop and remove ldw-static-files
	docker rm -f ldw-static-files

	# Build patrickhoefler/linked-data-wizards-nginx
	docker build --tag=patrickhoefler/linked-data-wizards-nginx .

	# Clean up
	rm -rf static

.PHONY: test
test:
	# List the static files in the built image
	docker run --rm patrickhoefler/linked-data-wizards-nginx ls /usr/share/nginx/html/static

	# List replace-and-run.sh
	docker run --rm patrickhoefler/linked-data-wizards-nginx ls -la /replace-and-run.sh

.PHONY: push
push:
	# Push the Docker image to the registry
	docker push patrickhoefler/linked-data-wizards-nginx
