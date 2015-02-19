#!/bin/bash

(
	which git && which docker && which docker-compose
) || (
	echo "Depended executable not found. Check the message above" && exit 1
) &&

SCRIPT_DIR=$(readlink -e $(dirname "$0"))
cd $SCRIPT_DIR/../docker &&

. ./docker-compose.yml.sh > ./docker-compose.yml &&
docker-compose up
