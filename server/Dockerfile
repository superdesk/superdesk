# import base image
FROM ubuntu:vivid

# install python3 and the build-time dependencies for c modules
RUN apt-get update && \
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
python3 python3-dev python3-pip python3-lxml \
build-essential libffi-dev git \
libtiff5-dev libjpeg8-dev zlib1g-dev \
libfreetype6-dev liblcms2-dev libwebp-dev \
libmagic-dev \
curl

# Set the locale
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# setup the environment
WORKDIR /opt/superdesk/
CMD ["honcho", "start"]

EXPOSE 5000
EXPOSE 5050
EXPOSE 5100

ENV PYTHONUNBUFFERED 1
ENV C_FORCE_ROOT "False"
ENV CELERYBEAT_SCHEDULE_FILENAME /tmp/celerybeatschedule.db

# install dependencies
ADD requirements.txt /tmp/requirements.txt
RUN cd /tmp && pip3 install -U -r /tmp/requirements.txt

# copy application source code
ADD . /opt/superdesk
