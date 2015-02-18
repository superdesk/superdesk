#!/bin/sh
docker rmi $(docker images | grep "^<none>" | sed -r 's/[   ]+/ /g' | cut -d' ' -f3)
