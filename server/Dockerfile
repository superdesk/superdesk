FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive 

RUN apt-get update && apt-get install -y --no-install-recommends \
python3 python3-dev python3-pip git gcc mongo-tools mongodb-clients curl \
# lxml
libxml2-dev libxslt-dev \
# PIL
libjpeg-dev zlib1g-dev \
# magic
libmagic-dev \
&& rm -rf /var/lib/apt/lists/* 

# install server
WORKDIR /opt/superdesk/
COPY requirements.txt .
RUN python3 -m pip install -U pip wheel setuptools && \
python3 -m pip install -Ur requirements.txt

ENV PYTHONUNBUFFERED=1
ENV C_FORCE_ROOT=False

COPY . .

ENTRYPOINT [ "/opt/superdesk/docker/start.sh" ]
CMD ["honcho", "start"]
