FROM caltha/protractor:latest
RUN apt-get update ; apt-get install -y git
WORKDIR /opt/superdesk-client
COPY ./client/package.json /opt/superdesk-client/
RUN cd /opt/superdesk-client && npm install && ./node_modules/.bin/webdriver-manager update
COPY ./client /opt/superdesk-client
