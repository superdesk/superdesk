#!/bin/bash

set -e

# unit test
./node_modules/karma/bin/karma start --single-run --browsers PhantomJS --reporters dots

# code style checks
grunt ci
