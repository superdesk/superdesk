# import base image
FROM ubuntu:trusty

# install python3 and build dependencies for c modules
RUN	apt-get update && \
	DEBIAN_FRONTEND=noninteractive apt-get upgrade -y && \
	DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
	python3 python3-dev python3-pip \
	gcc libffi-dev git mercurial
# update pip and distribute
RUN	pip3 install -U pip distribute

# install dependencies
COPY	./requirements.txt /opt/superdesk/
RUN	pip install -U gunicorn && \
	pip install -r /opt/superdesk/requirements.txt

# copy superdesk source code
COPY	. /opt/superdesk

# setup the environment
WORKDIR	/opt/superdesk/
EXPOSE	5000
EXPOSE	5100

CMD ["honcho", "start"]
