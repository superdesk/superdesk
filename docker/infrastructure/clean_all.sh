#!/bin/sh
SCRIPT_PATH=$(readlink -e $(dirname "$0"))
$SCRIPT_PATH/clean_images.sh
$SCRIPT_PATH/clean_containers.sh
$SCRIPT_PATH/clean_images.sh
