#!/bin/bash

set -e

# unit test via phantom
./node_modules/karma/bin/karma start --single-run --browsers PhantomJS

# code style checks
grunt hint
