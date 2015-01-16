#!/bin/bash

# Count how often we have tried to connect to Virtuoso
TIMEOUT_COUNTER=0

# Check if Virtuoso is ready
echo 'Granting SPARQL update rights in Virtuoso ...'
sleep 3

while ! isql-vt exec='select 1;' &> /dev/null; do
  if ((TIMEOUT_COUNTER == 0)); then
    echo 'Waiting for Virtuoso ...'
  elif ((TIMEOUT_COUNTER < 10)); then
    echo 'Still waiting for Virtuoso ...'
  elif ((TIMEOUT_COUNTER == 10)); then
    echo 'Virtuoso failed to respond, giving up.' >&2
    exit 1
  fi

  ((TIMEOUT_COUNTER++))
  sleep 3
done

# Grant SPARQL update rights
isql-vt exec='grant SPARQL_UPDATE to "SPARQL";' &> /dev/null
