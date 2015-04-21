# Superdesk [![Build Status](https://travis-ci.org/superdesk/superdesk.png?branch=master)] (https://travis-ci.org/superdesk/superdesk)

Superdesk is an open source end-to-end news creation, production, curation,
distribution and publishing platform developed and maintained by Sourcefabric
with the sole purpose of making the best possible software for journalism. It
is scaleable to suit news organizations of any size.

### Installation

Use [docker-compose](http://fig.sh "") and the config from `docker` folder or build docker images manually from `Dockerfile`s from `client` and `server` folders accordingly.

##### install docker and virtualenv

```sh
$ sudo apt-get install docker.io
$ sudo apt-get install python-virtualenv
```

and make sure you can run [docker without sudo](http://askubuntu.com/questions/477551/how-can-i-use-docker-without-sudo).


##### install docker compose and run app

_should be executed inside the repository root:_

```sh
$ virtualenv env
$ . env/bin/activate
$ pip install -r docker/requirements.txt
$ ./scripts/docker-local-demo.sh
```

If you're going to assign some hostname to the instance, you should also set it in the config here https://github.com/superdesk/superdesk/blob/master/docker/docker-compose.yml.sh#L44-L45 and here https://github.com/superdesk/superdesk/blob/master/docker/docker-compose.yml.sh#L55 instead of `127.0.0.1`.

For manual installation just follow the steps described in both [client](./client/Dockerfile) and [server](./server/Dockerfile) Dockerfiles.
