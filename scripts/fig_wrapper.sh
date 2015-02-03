#!/bin/sh

TIMEOUT=2

LISTEN=0
while [ $LISTEN -eq 0 ]
do
	echo "waiting..."
	LISTEN=1
	curl -m $TIMEOUT db:27017 || LISTEN=0
	curl -m $TIMEOUT redis:6379 | grep "wrong number of arguments for 'get' command" || LISTEN=0
	curl -m $TIMEOUT elastic:9200 || LISTEN=0
done
echo "All services are started :3"

cd $(readlink -e $(dirname "$0")/../) &&
"$@" &&
exit 0
