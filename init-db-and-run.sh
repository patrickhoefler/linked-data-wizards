#!/bin/bash

# Initialize the DB
./init-db.sh

# Start the green unicorn
gunicorn --bind 0.0.0.0:8000 --error-logfile - --access-logfile - ldva.wsgi
