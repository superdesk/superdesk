# Superdesk
[![Build Status](https://travis-ci.org/superdesk/superdesk.png?branch=master)](https://travis-ci.org/superdesk/superdesk)
[![Code Health](https://landscape.io/github/superdesk/superdesk/master/landscape.svg?style=flat)](https://landscape.io/github/superdesk/superdesk/master)
[![Coverage Status](https://coveralls.io/repos/superdesk/superdesk/badge.svg)](https://coveralls.io/r/superdesk/superdesk)
[![Code Climate](https://codeclimate.com/github/superdesk/superdesk/badges/gpa.svg)](https://codeclimate.com/github/superdesk/superdesk)
[![Requirements Status](https://requires.io/github/superdesk/superdesk/requirements.svg?branch=master)](https://requires.io/github/superdesk/superdesk/requirements/?branch=master)

Superdesk is an open source end-to-end news creation, production, curation,
distribution and publishing platform developed and maintained by Sourcefabric
with the sole purpose of making the best possible software for journalism. It
is scaleable to suit news organizations of any size. See the [Superdesk website] (http://www.superdesk.org) for more information.

Looking to stay up to date on the latest news? [Subscribe] (http://eepurl.com/bClQlD) to our monthly newsletter. 

The Superdesk server provides the API to process all client requests. The client 
provides the user interface. Server and client are separate applications using 
different technologies.

Find more information about the client configuration in the README file of the repo:
[https://github.com/superdesk/superdesk-client-core](https://github.com/superdesk/superdesk-client-core "") 

### Installation

Use [docker-compose](http://docs.docker.com/compose/ "") and the config from the `docker` folder or build docker images manually from `Dockerfile`s from `client` and `server` folders accordingly.

##### install system-wide dependencies

```sh
$ sudo apt-get install python-virtualenv git
```
and install [the newest docker](https://docs.docker.com/installation/).
and make sure you can run [docker without sudo](http://askubuntu.com/questions/477551/how-can-i-use-docker-without-sudo).


##### install docker compose and run app

```sh
$ git clone https://github.com/superdesk/superdesk.git
$ cd superdesk
$ git clone https://github.com/superdesk/superdesk-content-api.git
$ ./scripts/docker-local-demo.sh
```

Open in a browser `http://localhost:80` after the server will be ready.

If you can't log in then you probably need to run `./scripts/docker-local-create-user.sh`. The default username is `admin` and the password is `admin`.

If you're going to assign some hostname to the instance, you should also set it in the config file  [common.yml](./docker/common.yml) instead of `127.0.0.1`.

For manual installation just follow the steps described in the [Dockerfile](./Dockerfile).

###Contribute

In general, contributing code to the Superdesk project – whether it is a new feature or a bug fix – is simple and follows this general path:

1) Get a copy of the project source code 
<P>2) Work on the code changes</P>
<P>3) Submit a Pull Request whenever you are ready</P>

###Questions and issues

Our [issue tracker] (https://dev.sourcefabric.org/projects/SD) is only for bug reports and feature requests. Anything else, such as questions or general feedback, should be posted in the [forum] (https://forum.sourcefabric.org/categories/superdesk-dev).

###A special thanks to...

Users, developers and development partners that have contributed to the Superdesk project. Also, to all the other amazing open-source projects that make Superdesk possible!

###License

Superdesk is available under the [AGPL version 3] (https://www.gnu.org/licenses/agpl-3.0.html) open source license.
