#!/bin/bash

WORK_DIR=$(readlink -e $(dirname "$0"))

(test -d $WORK_DIR/env || virtualenv -p python2 $WORK_DIR/env ) &&
. $WORK_DIR/env/bin/activate &&
pip install -r $WORK_DIR/../docker/requirements.txt &&

(
	docker --version && docker ps >/dev/null && docker-compose --version
) || (
	echo "Depended executable not found. Check the message above" && exit 1
) &&

cd $WORK_DIR/../docker &&

echo '
|=================================================================|
|open in browser "http://localhost:80" after server will be ready |
|                                                                 |
|       if you can not log in you probably need to run            |
|       "./docker-local-create-user.sh"                           |
|=================================================================|
' &&
docker-compose build &&
docker-compose up --timeout 600
