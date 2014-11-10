#!/bin/sh

#protractor protractor-conf.js \
./node_modules/.bin/protractor protractor-conf.js \
  --specs "spec/setup.js,spec/matchers.js,spec/login_spec.js" \
  --stackTrace --verbose \
  --params.baseUrl 'https://master.sd-test.sourcefabric.org' \
  --params.baseBackendUrl 'https://master.sd-test.sourcefabric.org/api' \
  --params.username 'new_one' \
  --params.password 'new_one'
