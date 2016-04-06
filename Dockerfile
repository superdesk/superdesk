# import base image
FROM ubuntu:trusty

# install system-wide dependencies,
# python3 and the build-time dependencies for c modules
RUN apt-get update && \
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
python3 python3-dev python3-pip python3-lxml \
build-essential libffi-dev git \
libtiff5-dev libjpeg8-dev zlib1g-dev \
libfreetype6-dev liblcms2-dev libwebp-dev \
curl libfontconfig nodejs npm nginx \
&& echo "\ndaemon off;" >> /etc/nginx/nginx.conf \
&& rm /etc/nginx/sites-enabled/default \
&& ln --symbolic /usr/bin/nodejs /usr/bin/node

RUN npm install -g npm
RUN npm -g install grunt-cli bower

# Set the locale
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

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

# set env vars for the server
ENV PYTHONUNBUFFERED 1
ENV C_FORCE_ROOT "False"
ENV CELERYBEAT_SCHEDULE_FILENAME /tmp/celerybeatschedule.db

# install server dependencies
COPY ./server/requirements.txt /tmp/requirements.txt
RUN cd /tmp && pip3 install -U -r /tmp/requirements.txt

# install client dependencies
COPY ./client/package.json /opt/superdesk/client/
RUN cd ./client && npm install
COPY ./client/bower.json /opt/superdesk/client/
COPY ./client/.bowerrc /opt/superdesk/client/
RUN cd ./client && bower --allow-root install

# copy server sources
COPY ./server /opt/superdesk

# copy client sources
COPY ./client /opt/superdesk/client

RUN cd ./client && grunt build
