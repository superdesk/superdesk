#!/bin/bash

set -e

# build
grunt build

# deploy
rsync -ave ssh dist/* lab:superdesk/devel/
