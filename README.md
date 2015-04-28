# Superdesk [![Build Status](https://travis-ci.org/superdesk/superdesk.png?branch=master)] (https://travis-ci.org/superdesk/superdesk)

Superdesk is an open source end-to-end news creation, production, curation,
distribution and publishing platform developed and maintained by Sourcefabric
with the sole purpose of making the best possible software for journalism. It
is scaleable to suit news organizations of any size.

### Installation

Use [docker-compose](http://fig.sh "") and the config from `docker` folder or build docker images manually from `Dockerfile`s from `client` and `server` folders accordingly.

##### install system-wide dependencies

```sh
$ sudo apt-get install docker.io python2 python-virtualenv
```

and make sure you can run [docker without sudo](http://askubuntu.com/questions/477551/how-can-i-use-docker-without-sudo).


##### install docker compose and run app

```sh
$ git clone https://github.com/superdesk/superdesk.git
$ cd superdesk
$ ./scripts/docker-local-demo.sh
```

Open in browser `http://localhost:80` after server will be ready.

If you can not log in you probably need to run `./scripts/docker-local-create-user.sh`.

If you're going to assign some hostname to the instance, you should also set it in the config here https://github.com/superdesk/superdesk/blob/master/docker/docker-compose.yml.sh#L44-L45 and here https://github.com/superdesk/superdesk/blob/master/docker/docker-compose.yml.sh#L55 instead of `127.0.0.1`.

For manual installation just follow the steps described in both [client](./client/Dockerfile) and [server](./server/Dockerfile) Dockerfiles.
