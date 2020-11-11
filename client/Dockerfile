# BUILD
FROM node:lts AS build

# install client
WORKDIR /tmp/client
RUN npm install -g grunt-cli
COPY package.json .
RUN npm install --no-audit
COPY . .
RUN npx grunt build

# DEPLOY
FROM nginx

# setup the environment
WORKDIR /opt/superdesk/client/dist

# build client
COPY --from=build /tmp/client/dist ./

RUN rm /etc/nginx/conf.d/default.conf
COPY ./docker/nginx.conf /etc/nginx/nginx.conf
COPY ./docker/superdesk_vhost.conf /etc/nginx/sites-enabled/superdesk.conf
COPY ./docker/start.sh /opt/superdesk/start.sh

ENTRYPOINT [ "/opt/superdesk/start.sh" ]
CMD ["nginx", "-g daemon off;"]
