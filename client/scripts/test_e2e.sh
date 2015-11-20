#!/usr/bin/env bash

# check if we should only run a single test
SINGLE_TEST=$1

# prepare server
grunt clean
grunt server:travis &

# wait for server to be ready
while [ ! -f $(dirname "$0")/../dist/index.html ]; do
    sleep .5
done

# run tests
./node_modules/protractor/bin/webdriver-manager update
if [ -z "$SINGLE_TEST" ]; then
    echo "Running full test suite"
    ./node_modules/protractor/bin/protractor protractor-conf.js --baseUrl 'http://localhost:9000'
else
    echo "Running single test: $SINGLE_TEST"
    ./node_modules/protractor/bin/protractor protractor-conf.js --spec $SINGLE_TEST --baseUrl 'http://localhost:9000'
fi
TEST_STATUS=$?

# stop server
kill $!

# return test status
exit $TEST_STATUS
