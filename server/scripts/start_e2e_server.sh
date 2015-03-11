#!/bin/bash

cat >/tmp/testenv <<EOF
SUPERDESK_TESTING=true
MONGO_DBNAME=superdesk_e2e
ELASTICSEARCH_INDEX=superdesk_e2e
REDIS_URL=redis://localhost:6379/2
EOF

honcho -e /tmp/testenv run python manage.py users:create -u admin -p admin -e admin@localhost --admin=true
honcho -e /tmp/testenv start
rm -f /tmp/testenv
