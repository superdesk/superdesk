#!/usr/bin/env bash

# prepare server
grunt clean
grunt server:travis &

# wait for server to be ready
while [ ! -f $(dirname "$0")/../dist/index.html ]; do
    sleep .5
done

# run tests
./node_modules/protractor/bin/webdriver-manager update
./node_modules/protractor/bin/protractor protractor-conf.js --baseUrl 'http://localhost:9000'
TEST_STATUS=$?

# stop server
kill $!

# return test status
exit $TEST_STATUS
