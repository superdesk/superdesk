FROM ubuntu:16.04

ENV DEBIAN_FRONTEND=noninteractive 

RUN apt-get update && apt-get install -y --no-install-recommends \
python3 python3-dev python3-pip python3-venv python3-wheel \
git gcc curl \
# lxml
libxml2-dev libxslt-dev \
# PIL
libjpeg-dev zlib1g-dev \
# magic
libmagic-dev \
&& rm -rf /var/lib/apt/lists/* 

WORKDIR /opt/superdesk

# this will activate env for the following commands
ENV VIRTUAL_ENV=/opt/superdesk/env
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install pip==20.3.4
RUN pip3 install setuptools
RUN pip3 install wheel

COPY requirements.txt .

RUN pip3 install -U -r /opt/superdesk/requirements.txt
RUN pip3 install -U honcho gunicorn
