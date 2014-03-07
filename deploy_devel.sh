#!/bin/bash

set -e

# build
grunt build --server='http://apytest.apy.sd-test.sourcefabric.org'

# deploy
rsync -ave ssh dist/* lab:superdesk/devel/
