#!/bin/bash

cat >/tmp/testenv <<EOF
SUPERDESK_TESTING=true
MONGO_DBNAME=superdesk_e2e
ELASTICSEARCH_INDEX=superdesk_e2e
LEGAL_ARCHIVE_DBNAME=superdesk_e2e_legal_archive
LEGAL_ARCHIVE=true
ARCHIVED_DBNAME=superdesk_e2e_archived
REDIS_URL=redis://localhost:6379/2
WEB_CONCURRENCY=3
WEB_TIMEOUT=5

EOF

honcho -e /tmp/testenv start
rm -f /tmp/testenv
