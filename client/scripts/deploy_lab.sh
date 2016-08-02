#!/bin/bash

set -e

# build
grunt build --server="http://superdesk-api.herokuapp.com"

# deploy
rsync -ave ssh dist/* lab:superdesk/
