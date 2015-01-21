#!/bin/bash

# Dump all registered SPARQL endpoints
python manage.py dumpdata sparql.Endpoint > ldva/libs/sparql/fixtures/endpoints.json --indent=2
