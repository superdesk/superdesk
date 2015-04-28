#!/bin/bash

(
	docker --version && docker ps >/dev/null && docker-compose --version
) || (
	echo "Depended executable not found. Check the message above" && exit 1
) &&

cd $(dirname "$0")/../docker &&

. ./docker-compose.yml.sh > ./docker-compose.yml &&
echo '
|=================================================================|
|open in browser "http://localhost:80" after server will be ready |
|                                                                 |
|       if you can not log in you probably need to run            |
|       "./docker-local-create-user.sh"                           |
|=================================================================|
' &&
docker-compose build &&
docker-compose up --no-recreate --timeout 600
