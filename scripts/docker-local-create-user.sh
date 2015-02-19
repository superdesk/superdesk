#!/bin/sh
SCRIPT_DIR=$(readlink -e $(dirname "$0"))
cd $SCRIPT_DIR/../docker &&
docker-compose run backend ./scripts/fig_wrapper.sh python3 manage.py users:create -u admin -p admin -e 'admin@example.com' --admin=true
