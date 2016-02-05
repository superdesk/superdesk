#!/bin/sh
script_dir=$(readlink -e $(dirname "$0"))
$script_dir/../server/scripts/generate-docker-docs.py $script_dir/../Dockerfile > $script_dir/../INSTALL.md
