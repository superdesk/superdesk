#!/bin/sh

cd $(dirname "$0")/../client/

echo -n 'wait for client.'
while ! curl -sfo /dev/null 'http://127.0.0.1/'; do echo -n '.' && sleep .5; done
echo 'done.'

npm install --unsafe-perm=true &&
./node_modules/.bin/webdriver-manager update &&
xvfb-run --server-args="-screen 0, 1920x1080x24" --auto-servernum \
./node_modules/.bin/protractor protractor.conf.js \
  --stackTrace --verbose \
  --baseUrl 'http://127.0.0.1' \
  --params.baseBackendUrl 'http://127.0.0.1/api' \
  --params.username 'admin' \
  --params.password 'admin'
