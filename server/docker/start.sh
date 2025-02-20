#!/bin/bash
set -e

cd /opt/superdesk/

# wait for elastic to be up
printf 'waiting for elastic.'
until $(curl --output /dev/null --silent --head --fail "${ELASTICSEARCH_URL}"); do
    printf '.'
    sleep .5
done
echo 'done.'

# init app
honcho run python3 manage.py app:initialize_data

# make sure there is admin:admin user
honcho run python3 manage.py users:create -u admin -p admin -e admin@localhost --admin

exec "$@"
