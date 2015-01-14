#!/bin/bash

# Update nginx config with the host and the port of the ldw-gunicorn service
sed -i.bak 's/{{$LDW_GUNICORN_SERVICE_HOST}}/'"$LDW_GUNICORN_SERVICE_HOST"'/' /etc/nginx/nginx.conf
sed -i.bak 's/{{$LDW_GUNICORN_SERVICE_PORT}}/'"$LDW_GUNICORN_SERVICE_PORT"'/' /etc/nginx/nginx.conf

# Start nginx
nginx -g 'daemon off;'
