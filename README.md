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

## Installation

### Client

1. Clone the repository
2. Navigate to the folder where you've cloned this repository (if it's the main repo, go inside the `client` folder).
3. Run `npm install` to install dependencies.
4. Run `grunt server` to run the web server.
5. Open browser and navigate to `localhost:9000`.

The `grunt server` attempts to resolve the API and websockets server to a local instance. In order to use a different instance, you may add the arguments `--server=<host:[port]>` and `--ws=<host:[port]>` to the command.

### Server

#### Dependencies (for non-Docker installations)

* Python & Pyvenv 3+
* MongoDB
* ElasticSearch <= 1.7.x
* Redis

#### MacOS

For the sake of this walkthrough, it is considered that your python binary is called `python3`. Please amend as needed for your own system.

1. Install dependencies using `brew` (make sure you do a `brew update` first): `python3`, `mongodb`, `elasticsearch`, `redis`.
2. Create a virtual envirnoment in a folder of your choice, for example `mkdir ~/pyvenv && pyvenv-3.5 ~/pyvenv`.
3. Activate the environment by running its activation script: `. ~/pyvenv/bin/activate`. All of the following steps need to run under the virtual environment.
4. Install _pip_ dependencies by running (inside repository root): `pip install -r server/requirements.txt`.
5. Start all dependent services: `mongod`, `redis-server`, `elasticsearch`.
6. For an initially empty database, you may initialize and pre-populate it by running (inside the `server` folder): `python3 manage.py app:initialize_data && python3 manage.py app:prepopulate`.
7. Finally, start the server (inside the `server` folder) using `honcho start`.

#### Linux (with Docker)

Use [docker-compose](http://docs.docker.com/compose/ "") and the config from the `docker` folder or build docker images manually from `Dockerfile`s from `client` and `server` folders accordingly.

###### install system-wide dependencies

```sh
$ sudo apt-get install python-virtualenv git
```
and install [the newest docker](https://docs.docker.com/installation/).
and make sure you can run [docker without sudo](http://askubuntu.com/questions/477551/how-can-i-use-docker-without-sudo).


###### install docker compose and run app

```sh
$ git clone https://github.com/superdesk/superdesk.git
$ cd superdesk
$ git clone https://github.com/superdesk/superdesk-content-api.git
$ ./scripts/docker-local-demo.sh
```

Open in a browser `http://localhost:8080` after the server will be ready.

If you can't log in then you probably need to run `./scripts/docker-local-create-user.sh`. The default username is `admin` and the password is `admin`.

If you're going to assign some hostname to the instance, you should also set it in the config file [docker-compose-prebuilt.yml](./docker/docker-compose-prebuilt.yml) instead of `localhost`.

For manual installation just follow the steps described in the [Dockerfile](./Dockerfile).

###Contribute

In general, contributing code to the Superdesk project – whether it is a new feature or a bug fix – is simple and follows this general path:

1) Get a copy of the project source code or [setup a dev environment with docker](DEVSETUP.md)
<P>2) Work on the code changes</P>
<P>3) Submit a Pull Request whenever you are ready</P>

###Questions and issues

Our [issue tracker] (https://dev.sourcefabric.org/projects/SD) is only for bug reports and feature requests. Anything else, such as questions or general feedback, should be posted in the [forum] (https://forum.sourcefabric.org/categories/superdesk-dev).

###A special thanks to...

Users, developers and development partners that have contributed to the Superdesk project. Also, to all the other amazing open-source projects that make Superdesk possible!

###License

Superdesk is available under the [AGPL version 3] (https://www.gnu.org/licenses/agpl-3.0.html) open source license.
