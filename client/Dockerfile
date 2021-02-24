FROM ubuntu:16.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
nodejs npm git gcc curl \
&& rm -rf /var/lib/apt/lists/*

RUN npm install -g n
RUN n 12
RUN npm install -g grunt-cli bufferutil

COPY . .
RUN npm install --no-audit

RUN npx grunt build
