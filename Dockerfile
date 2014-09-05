# import base image
FROM ubuntu:trusty

# install python3 and build dependencies for c modules
RUN	apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3 python3-dev python3-pip \
    build-essential libffi-dev libjpeg8-dev \
    git mercurial

# update pip and distribute
RUN	pip3 install -U pip distribute

# install dependencies
ADD requirements.txt /tmp/requirements.txt
RUN pip install -U -r /tmp/requirements.txt

ENV C_FORCE_ROOT "False"

# setup the environment
ADD . /opt/superdesk
WORKDIR	/opt/superdesk/
EXPOSE	5000
EXPOSE	5100

ENTRYPOINT ["honcho"]
CMD ["start"]
