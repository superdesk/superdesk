# Superdesk

Superdesk is an open source end-to-end news creation, production, curation,
distribution and publishing platform developed and maintained by Sourcefabric
with the sole purpose of making the best possible software for journalism. It
is scaleable to suit news organizations of any size.

### Installation

You can use docker to install the app and its required services - mongodb, elasticsearch and redis.

##### install docker

```sh
$ sudo apt-get install docker.io
```

and make sure you can run [docker without sudo](http://askubuntu.com/questions/477551/how-can-i-use-docker-without-sudo).

##### create python virtualenv

```sh
$ sudo apt-get install python-virtualenv
$ virtualenv env
```

##### install docker compose and run app

```sh
$ . env/bin/activate
$ pip install -r docker/requirements.txt
$ ./scripts/docker-local-demo.sh
```

For manual installation just follow the steps described both [client](./client/Dockerfile) and [server](./server/Dockerfile) Dockerfiles.
