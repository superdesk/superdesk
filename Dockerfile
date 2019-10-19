# import base image
FROM ubuntu:bionic

# install system-wide dependencies,
# python3 and the build-time dependencies for c modules
RUN apt-get update && \
  DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  python3 python3-dev python3-pip python3-lxml \
  build-essential libffi-dev git locales \
  libtiff5-dev libjpeg8-dev zlib1g-dev libmagic-dev \
  libfreetype6-dev liblcms2-dev libwebp-dev \
  curl libfontconfig nginx \
  libxml2-dev libxslt1-dev \
  && rm /etc/nginx/sites-enabled/default
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -
RUN apt-get install -y --no-install-recommends \
  nodejs

# Set the locale
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
ENV TZ Europe/London

# setup the environment
WORKDIR /opt/superdesk/
COPY ./docker/nginx.conf /etc/nginx/nginx.conf
COPY ./docker/superdesk_vhost.conf /etc/nginx/sites-enabled/superdesk.conf
COPY ./docker/start.sh /opt/superdesk/start.sh
CMD /opt/superdesk/start.sh

# client ports
EXPOSE 9000
EXPOSE 80

# server ports
EXPOSE 5000
EXPOSE 5100
EXPOSE 5400

# set env vars for the server
ENV PYTHONUNBUFFERED 1
ENV C_FORCE_ROOT "False"
ENV CELERYBEAT_SCHEDULE_FILENAME /tmp/celerybeatschedule.db

# install server
COPY ./server /opt/superdesk
RUN python3 -m pip install --upgrade pip setuptools wheel
RUN python3 -m pip install -U -r requirements.txt --ignore-installed

# install client
COPY ./client /opt/superdesk/client/
RUN npm install -g npm grunt-cli
RUN cd ./client && npm install && grunt build

# copy git revision informations (used in "about" screen)
COPY .git/HEAD /opt/superdesk/.git/
COPY .git/refs/ /opt/superdesk/.git/refs/
