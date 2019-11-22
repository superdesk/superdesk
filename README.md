# Superdesk
[![Build Status](https://travis-ci.org/superdesk/superdesk.png?branch=master)](https://travis-ci.org/superdesk/superdesk)
[![Code Health](https://landscape.io/github/superdesk/superdesk/master/landscape.svg?style=flat)](https://landscape.io/github/superdesk/superdesk/master)
[![Coverage Status](https://coveralls.io/repos/superdesk/superdesk/badge.svg)](https://coveralls.io/r/superdesk/superdesk)
[![Code Climate](https://codeclimate.com/github/superdesk/superdesk/badges/gpa.svg)](https://codeclimate.com/github/superdesk/superdesk)
[![Requirements Status](https://requires.io/github/superdesk/superdesk/requirements.svg?branch=master)](https://requires.io/github/superdesk/superdesk/requirements/?branch=master)

Superdesk is an open source end-to-end news creation, production, curation,
distribution and publishing platform developed and maintained by Sourcefabric
with the sole purpose of making the best possible software for journalism. It
is scaleable to suit news organizations of any size. See the [Superdesk website](http://www.superdesk.org) for more information.

Looking to stay up to date on the latest news? [Subscribe](http://eepurl.com/bClQlD) to our monthly newsletter.

The Superdesk server provides the API to process all client requests. The client
provides the user interface. Server and client are separate applications using
different technologies.

Find more information about the client configuration in the README file of the repo:
[github.com/superdesk/superdesk-client-core](https://github.com/superdesk/superdesk-client-core)

## Simple installation

An environment variable, ```DOCKER_IP```, is required for Superdesk to know where it is hosted. This can be found by using the ```docker-machine env``` command. If you are using a virtual machine, its address may change between restarts, and therefore it is recommended to re-set the variable in every shell you open.

**This is not suitable for production use**. In production, disable the included Postfix email server and point the environment variables to a properly managed server. You'd definitely also want to be storing media on an S3 compatible service, and take regular backups, features which aren't included in this installation.

```sh
# Set DOCKER_IP environment variable
docker-machine env
export DOCKER_IP=192.168.xxx.xxx

# Install and run superdesk with services
git clone https://github.com/superdesk/superdesk
cd superdesk
docker compose -f docker/docker-compose.yml up -d

# Open shell in superdesk container
docker exec -it superdesk bash

# Configure superdesk
cd /opt/superdesk
python3 manage.py users:create -u 'username' -p 'password' -e 'email' --admin

# Prepopulate data (for testing)
python3 manage.py app:prepopulate_data
```
Superdesk will be accessible on ```http://DOCKER_IP:80```.

Building the ```superdesk``` image may take a while and can be memory intensive (> 2GB).

## Custom installation
At the bare minimum, Superdesk requires these services to run:
- MongoDB
- ElasticSearch (1.7.x - 2.4.x)
- Redis
- Python (>= 3.5)
- Node.js (with `npm`)
- SMTP Email Server

You'll probably also want these:
- AWS S3 compatible storage account
- Logstash / Kibana for log processing
- A Highcharts licence for the analytics extension

To run the ```superdesk``` container as standalone (without ```docker-compose```), have a look through the environment variables that you'd need to set in ```docker/common.yml``` and ```docker/docker-compose.yml```.

Further settings can be found in the [server documentation](https://superdesk.readthedocs.io/en/latest/settings.html).

## Questions and issues

- Our [issue tracker](https://dev.sourcefabric.org/projects/SD) is only for bug reports and feature requests.
- Anything else, such as questions or general feedback, should be posted in the [forum](https://forum.sourcefabric.org/categories/superdesk-dev).

### A special thanks to...

Users, developers and development partners that have contributed to the Superdesk project. Also, to all the other amazing open-source projects that make Superdesk possible!

### License

Superdesk is available under the [AGPL version 3](https://www.gnu.org/licenses/agpl-3.0.html) open source license.
