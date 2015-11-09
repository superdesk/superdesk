#!/bin/sh
SCRIPT_DIR=$(readlink -e $(dirname "$0"))
(test -d $SCRIPT_DIR/env || virtualenv -p python2 $SCRIPT_DIR/env ) &&
. $SCRIPT_DIR/env/bin/activate
set -ue
pip install -r $SCRIPT_DIR/../docker/requirements.txt
cd $SCRIPT_DIR/../docker
docker-compose -p sddemo -f ./docker-compose-prebuilt.yml run backend ./scripts/fig_wrapper.sh python3 manage.py app:initialize_data
docker-compose -p sddemo -f ./docker-compose-prebuilt.yml run backend ./scripts/fig_wrapper.sh python3 manage.py users:create -u admin -p admin -e 'admin@example.com' --admin=true
docker-compose -p sddemo -f ./docker-compose-prebuilt.yml run pubapi ./scripts/fig_wrapper.sh python3 content_api_manage.py app:prepopulate
