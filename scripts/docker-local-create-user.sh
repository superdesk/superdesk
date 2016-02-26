#!/bin/sh
SCRIPT_DIR="$(echo $(cd -P -- "$(dirname -- "$0")" && pwd -P))"
(test -d $SCRIPT_DIR/env || virtualenv $SCRIPT_DIR/env ) &&
. $SCRIPT_DIR/env/bin/activate
set -ue
pip install -r $SCRIPT_DIR/../docker/requirements.txt
cd $SCRIPT_DIR/../docker


docker-compose -p sddemo -f ./docker-compose-prebuilt.yml run superdesk ./scripts/fig_wrapper.sh bash -c "\
  python3 manage.py app:initialize_data ;\
  echo '+++ sample data was prepopulated' ;\
  python3 manage.py users:create -u admin -p admin -e 'admin@example.com' --admin ;\
  echo '+++ new user has been created'"
docker-compose -p sddemo -f ./docker-compose-prebuilt.yml run pubapi bash ./scripts/fig_wrapper.sh bash -c "\
  python3 content_api_manage.py app:prepopulate ;\
  echo '+++ public api was prepopulated'"
