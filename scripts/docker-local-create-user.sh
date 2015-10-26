#!/bin/sh
SCRIPT_DIR=$(readlink -e $(dirname "$0"))
(test -d $SCRIPT_DIR/env || virtualenv -p python2 $SCRIPT_DIR/env ) &&
. $SCRIPT_DIR/env/bin/activate &&
pip install -r $SCRIPT_DIR/../docker/requirements.txt &&
cd $SCRIPT_DIR/../docker &&
docker-compose -p sddemo -f ./docker-compose-prebuilt.yml run backend ./scripts/fig_wrapper.sh python3 manage.py users:create -u admin -p admin -e 'admin@example.com' --admin=true
