#!/bin/sh

TIMEOUT=2

MONGO=0
REDIS=0
ELASTIC=0
while [ $MONGO -eq 0 ] || [ $ELASTIC -eq 0 ] || [ $REDIS -eq 0 ]
do
	if [ $MONGO -eq 0 ] ; then
		curl -s -m $TIMEOUT mongodb:27017 2>&1 > /dev/null &&
		MONGO=1 ||
		echo "waiting for mongo..."
	fi
	if [ $REDIS -eq 0 ] ; then
		curl -# -m $TIMEOUT redis:6379 2>&1 | grep "wrong number of arguments for 'get' command"  2>&1 > /dev/null &&
		REDIS=1 ||
		echo "waiting for redis..."
	fi
	if [ $ELASTIC -eq 0 ] ; then
		curl -s -m $TIMEOUT -o /dev/null elastic:9200  2>&1 > /dev/null &&
		ELASTIC=1 ||
		echo "waiting for elastic..."
	fi
	sleep 0.2
done
echo "All services are started :3"

cd $(readlink -e $(dirname "$0")/../) &&
"$@" &&
exit 0
