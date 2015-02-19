#!/bin/bash

(
	which docker && which docker-compose
) || (
	echo "Depended executable not found. Check the message above" && exit 1
) &&

SCRIPT_DIR=$(readlink -e $(dirname "$0")) &&
cd $SCRIPT_DIR/../docker &&

. ./docker-compose.yml.sh > ./docker-compose.yml &&
echo '|=================================================================|' &&
echo '|open in browser "http://localhost:80" after server will be ready |' &&
echo '|                                                                 |' &&
echo "|       if you can't log in you probably need to run              |" &&
echo '|       "./docker-local-create-user.sh" first                     |' &&
echo '|=================================================================|' &&
docker-compose up
