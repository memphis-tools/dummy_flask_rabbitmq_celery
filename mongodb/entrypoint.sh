#!/bin/bash

set -e

# Wait for MongoDB to be ready
sleep 5
echo "MongoDB should be up and running, we waited 5 seconds sir"

# Run the Python initialization script
. .venv/bin/activate
python3 /docker-entrypoint-initdb.d/init_mongo.py
