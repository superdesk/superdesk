FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive 

RUN apt-get update && apt-get install -y --no-install-recommends \
python3 python3-dev python3-pip python3-venv git gcc mongo-tools mongodb-clients curl \
# lxml
libxml2-dev libxslt-dev \
# PIL
libjpeg-dev zlib1g-dev \
# magic
libmagic-dev \
&& rm -rf /var/lib/apt/lists/* 

# setup venv
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv "$VIRTUAL_ENV"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# update venv
RUN python3 -m pip install -U pip wheel setuptools

# install server
WORKDIR /opt/superdesk/
COPY requirements.txt .
RUN python3 -m pip install -Ur requirements.txt

ENV PYTHONUNBUFFERED=1
ENV C_FORCE_ROOT=False
ENV CELERYBEAT_SCHEDULE_FILENAME=/tmp/celerybeatschedule.db
ENV TZ=Europe/London

COPY . .

ENTRYPOINT [ "/opt/superdesk/docker/start.sh" ]
CMD ["honcho", "start"]
