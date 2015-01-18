#!/bin/bash

# Initialize the DB
python manage.py syncdb --noinput
python manage.py loaddata endpoints
python manage.py loaddata datasets
