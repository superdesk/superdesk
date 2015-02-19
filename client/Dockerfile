# import base image
FROM dockerfile/nodejs

# install system-wide dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y libfreetype6 libfontconfig nginx && \
    echo "\ndaemon off;" >> /etc/nginx/nginx.conf && \
    rm /etc/nginx/sites-enabled/default && \
    npm -g install grunt-cli bower

# setup the environment
WORKDIR	/opt/superdesk-client/
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
