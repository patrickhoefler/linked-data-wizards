#!/bin/bash

# Define a timestamp function
timestamp() {
  date +"%H:%M:%S [Grant SPARQL Update rights]"
}

# Give Virtuoso a headstart
sleep 10

# Count how often we have tried to connect to Virtuoso
TIMEOUT_COUNTER=0

echo "$(timestamp) Connecting to Virtuoso ..."

while ! isql-vt exec='select 1;' &> /dev/null; do
  if ((TIMEOUT_COUNTER == 0)); then
    echo "$(timestamp) Waiting for Virtuoso ..."
  elif ((TIMEOUT_COUNTER < 10)); then
    echo "$(timestamp) Still waiting for Virtuoso ..."
  elif ((TIMEOUT_COUNTER == 10)); then
    echo "$(timestamp) Virtuoso failed to respond, giving up." >&2
    exit 1
  fi

  ((TIMEOUT_COUNTER++))
  sleep 3
done

echo "$(timestamp) Granting SPARQL update rights ..."
isql-vt exec='grant SPARQL_UPDATE to "SPARQL";'
