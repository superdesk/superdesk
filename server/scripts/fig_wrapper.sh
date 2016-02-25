#!/bin/sh

get_hostname() {
	echo $1 | sed -r 's/.*:\/\/([^:\/]*)[:\/].*/\1/g' 2>/dev/null
}

get_port() {
	result=$(
		echo $1 | sed -r '/.*:\/\/.*:(.*)(\/.*|$)/,${s//\1/;b};$q1' 2>/dev/null
	) && echo $result || echo "$2"
}

get_addr() {
	echo $(get_hostname "$1")":"$(get_port "$1" "$2")
}

global_timeout=120
ping_timeout=2

mongo_addr=$(get_addr "$MONGO_URI" 27017)
redis_addr=$(get_addr "$REDIS_URL" 6379)
elastic_addr=$(get_addr "$ELASTICSEARCH_URL" 9200)

mongo_is_listening=0
redis_is_listening=0
elastic_is_listening=0

start_time=$(date +%s)

while [ $mongo_is_listening -eq 0 ] || [ $elastic_is_listening -eq 0 ] || [ $redis_is_listening -eq 0 ]
do
	if [ $mongo_is_listening -eq 0 ] ; then
		curl -s -m $ping_timeout $mongo_addr 2>&1 > /dev/null &&
		mongo_is_listening=1 ||
		echo "waiting for mongo on $mongo_addr ..."
	fi
	if [ $redis_is_listening -eq 0 ] ; then
		curl -# -m $ping_timeout $redis_addr 2>&1 | grep "wrong number of arguments for 'get' command"  2>&1 > /dev/null &&
		redis_is_listening=1 ||
		echo "waiting for redis on $redis_addr ..."
	fi
	if [ $elastic_is_listening -eq 0 ] ; then
		curl -s -m $ping_timeout -o /dev/null $elastic_addr 2>&1 > /dev/null &&
		elastic_is_listening=1 ||
		echo "waiting for elastic on $elastic_addr ..."
	fi
	if [ $(expr $(date +%s) - $start_time) -gt $global_timeout ] ; then
		echo "Timeout ($global_timeout sec) exceeded."
		exit 1
	fi
	sleep 0.2
done
echo "All services are started :3"

cd $(readlink -e $(dirname "$0")/../) &&
"$@" &&
exit 0
