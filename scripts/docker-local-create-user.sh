#!/bin/bash

set -ue

SCRIPT_DIR="$(echo $(cd -P -- "$(dirname -- "$0")" && pwd -P))"

cd "$SCRIPT_DIR"/../docker

docker-compose -p sddemo -f ./docker-compose-prebuilt.yml run superdesk bash -c "\
  python3 manage.py app:initialize_data ;\
  echo '+++ sample data was prepopulated' ;\
  python3 manage.py users:create -u admin -p admin -e 'admin@example.com' --admin ;\
  echo '+++ new user has been created'"
