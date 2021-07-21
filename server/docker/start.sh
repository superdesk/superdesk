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

# init dbs
honcho run python3 manage.py app:initialize_data

if [[ -d dump ]] && [[ "${DEMO_DATA:0}" == "1" ]]; then
    echo 'installing demo data'
    mongorestore -h mongodb -d test --gzip dump
    honcho run python3 manage.py app:rebuild_elastic_index
else  # no dump, just create admin
    echo 'installing new instance'
    honcho run python3 manage.py users:create -u admin -p admin -e admin@localhost --admin
fi

exec "$@"
