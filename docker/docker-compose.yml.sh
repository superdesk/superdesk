cat <<EOF
mongodb:
  image: dockerfile/mongodb
  volumes:
   - ../data/mongodb:/data/db

redis:
  image: dockerfile/redis
  volumes:
   - ../data/redis:/data

elastic:
  image: dockerfile/elasticsearch
  volumes:
   - ../data/elastic:/data

backend:
  build: ../server
  command: sh /opt/superdesk/scripts/fig_wrapper.sh honcho start
  links:
   - mongodb
   - redis
   - elastic
  environment:
   - MONGOLAB_URI=mongodb://mongodb:27017/test
   - LEGAL_ARCHIVE_URI=mongodb://mongodb:27017/legal_test
   - ELASTICSEARCH_URL=http://elastic:9200
   - ELASTICSEARCH_INDEX
   - CELERY_BROKER_URL=redis://redis:6379/1
   - REDIS_URL=redis://redis:6379/1
   - AMAZON_ACCESS_KEY_ID
   - AMAZON_CONTAINER_NAME
   - AMAZON_REGION
   - AMAZON_SECRET_ACCESS_KEY
   - REUTERS_USERNAME
   - REUTERS_PASSWORD
   - MAIL_SERVER
   - MAIL_PORT
   - MAIL_USE_TLS
   - MAIL_USE_SSL
   - MAIL_USERNAME
   - MAIL_PASSWORD
   - SENTRY_DSN
   - SUPERDESK_URL=http://127.0.0.1/api
   - SUPERDESK_CLIENT_URL=http://127.0.0.1
   - SUPERDESK_TESTING=True
  volumes:
   - ../results/server/unit:/opt/superdesk/results-unit/
   - ../results/server/behave:/opt/superdesk/results-behave/

frontend:
  build: ../client
  environment:
   - EMBEDLY_KEY=$bamboo_EMBEDLY_KEY
  command: sh -c "grunt build --server='http://127.0.0.1/api' --ws='ws://127.0.0.1/ws' && nginx"
  volumes:
   - ../results/client/unit:/opt/superdesk-client/unit-test-results
  ports:
   - "443:443"
   - "80:80"
  links:
   - backend
EOF

# vim: set ft=yaml:
