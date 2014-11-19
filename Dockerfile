# import base image
FROM ubuntu:trusty

# install python3 and build dependencies for c modules
# update pip and distribute
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3 python3-dev python3-pip \
    build-essential libffi-dev libjpeg8-dev \
    git mercurial && \
    pip3 install -U pip distribute

# setup the environment
WORKDIR /opt/superdesk/
CMD ["honcho", "start"]
EXPOSE 5000
EXPOSE 5100
ENV C_FORCE_ROOT "False"

# install dependencies
ADD requirements.txt /tmp/requirements.txt
RUN pip install -U -r /tmp/requirements.txt

# copy application source code
ADD . /opt/superdesk
