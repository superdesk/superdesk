#!/bin/bash

set -e

# test
./node_modules/karma/bin/karma start --single-run --browsers PhantomJS --reporters dots

# hint
grunt jshint

# check style
grunt jscs
