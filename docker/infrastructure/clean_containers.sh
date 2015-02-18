#!/bin/sh
docker rm -v $(docker ps -a -q)
