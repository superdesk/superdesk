#!/bin/bash

set -ue

SCRIPT_DIR="$(echo $(cd -P -- "$(dirname -- "$0")" && pwd -P))"

function dcs() {
	docker-compose -p sddemo -f ./docker-compose-prebuilt.yml $@
}

(
	docker --version && docker ps >/dev/null && docker-compose --version
) || (
	echo "Depended executable not found. Install docker with docker-compose" && exit 1
) &&


echo '
|==================================================================|
|open in browser "http://localhost:8080" after server will be ready|
|                                                                  |
|       if you can not log in you probably need to run             |
|       "./docker-local-create-user.sh"                            |
|==================================================================|
'

cd "$SCRIPT_DIR"/../docker
dcs kill
dcs pull
dcs up --timeout 600
