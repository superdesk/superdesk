#!/bin/bash
set -e

cd /opt/superdesk/

# init dbs
honcho run python3 manage.py app:initialize_data

if [[ -d dump ]]
then
    mongorestore -h mongodb -d test --gzip dump
    honcho run python3 manage.py app:rebuild_elastic_index
else  # no dump, just create admin
    honcho run python3 manage.py users:create -u admin -p admin -e admin@localhost --admin
fi

exec "$@"
