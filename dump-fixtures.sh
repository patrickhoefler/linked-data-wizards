#!/bin/bash

# Dump all fixtures
python manage.py dumpdata sparql.Endpoint > ldva/libs/sparql/fixtures/endpoints.json --indent=2
python manage.py dumpdata sparql.Dataset > ldva/libs/sparql/fixtures/datasets.json --indent=2
