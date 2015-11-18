# import base image
FROM ubuntu:trusty

# install system-wide dependencies
RUN apt-get update && \
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
libfreetype6 libfontconfig nodejs npm nginx git \
&& echo "\ndaemon off;" >> /etc/nginx/nginx.conf \
&& rm /etc/nginx/sites-enabled/default \
&& ln --symbolic /usr/bin/nodejs /usr/bin/node

RUN npm -g install grunt-cli bower

# setup the environment
WORKDIR	/opt/superdesk-client/
COPY ./nginx.conf /etc/nginx/nginx.conf
COPY ./superdesk_vhost.conf /etc/nginx/sites-enabled/superdesk.conf
EXPOSE	9000
EXPOSE	80
CMD ["sh", "-c" "grunt build && nginx"]

# install app-wide dependencies
COPY ./package.json /opt/superdesk-client/
RUN npm install
COPY ./bower.json /opt/superdesk-client/
COPY ./.bowerrc /opt/superdesk-client/
RUN bower --allow-root install

# copy sources
COPY . /opt/superdesk-client
