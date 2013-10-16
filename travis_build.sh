#!/bin/bash

set -e

# test
./node_modules/.bin/karma start --single-run --browsers PhantomJS --reporters dots

# hint
grunt jshint
