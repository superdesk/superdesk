#!/bin/bash

set -e

# build
grunt build --server='https://apytest.apy.sd-test.sourcefabric.org/api'

# deploy
rsync -ave ssh dist/* lab:superdesk/devel/
