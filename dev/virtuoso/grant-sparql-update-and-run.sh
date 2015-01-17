#!/bin/bash

# Start script to grant SPARQL Update rights and send to background
/grant-sparql-update.sh &

# Start Virtuoso
virtuoso-t -f -c /etc/virtuoso-opensource-6.1/virtuoso.ini
