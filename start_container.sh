#!/bin/sh

INSTANCE=test

DOCKER_IF=$(ip addr show docker0 | sed -nr 's/.*inet[ ]+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\/.*/\1/p')
API_PORT=8080
WS_PORT=5100
SERVER_NAME=127.0.0.1:$API_PORT

docker run \
	-p $API_PORT:5000 \
	-p $WS_PORT:5100 \
	-e SUPERDESK_URL="https://$SERVER_NAME/api" \
	-e MONGOLAB_URI=mongodb://test:test@$DOCKER_IF:27017/superdesk \
	-e ELASTICSEARCH_URL=http://$DOCKER_IF:9200 \
	-e ELASTICSEARCH_INDEX="superdesk_$INSTANCE" \
	-e AMAZON_ACCESS_KEY_ID="" \
	-e AMAZON_CONTAINER_NAME="" \
	-e AMAZON_REGION="" \
	-e AMAZON_SECRET_ACCESS_KEY="" \
	-e CELERY_BROKER_URL="redis://$DOCKER_IF:6379/$REDIS_DB_ID" \
	-e CELERY_RESULT_BACKEND="redis://$DOCKER_IF:6379/$REDIS_DB_ID" \
	-e CELERY_ALWAYS_EAGER="False" \
	-e C_FORCE_ROOT="False" \
	-e REUTERS_USERNAME="" \
	-e REUTERS_PASSWORD="" \
	-e MAIL_SERVER="$DOCKER_IF" \
	-e MAIL_PORT="25" \
	-e MAIL_USE_TLS="false" \
	-e MAIL_USE_SSL="false" \
	-e MAIL_USERNAME="mail@$SERVER_NAME" \
	-e MAIL_PASSWORD="" \
	-e SENTRY_DSN="" \
	-i \
	-t superdesk-server:latest "$@"
