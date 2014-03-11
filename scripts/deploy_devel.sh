#!/bin/bash

set -e

# build
grunt build --server='//apytest.apy.sd-test.sourcefabric.org'

# deploy
rsync -ave ssh dist/* lab:superdesk/devel/
