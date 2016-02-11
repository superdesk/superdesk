# Superdesk Server [![Build Status](https://travis-ci.org/superdesk/superdesk-server.png?branch=master)](https://travis-ci.org/superdesk/superdesk-server) [![Code Health](https://landscape.io/github/superdesk/superdesk-server/master/landscape.svg)](https://landscape.io/github/superdesk/superdesk-server/master)

Superdesk Server provides a REST API server for [Superdesk project](https://wiki.sourcefabric.org/x/DgWX).
It's a python app, built on top of [eve](http://python-eve.org/)/[flask](http://flask.pocoo.org/) framework.

There is some basic infrastructure plus app modules for users, authentication, ingest, archive, etc.

## Requirements

We support python version 3.3+.

Other requirements are mongodb server and elasticsearch instance.
Both can be configured via environment variables (see [settings.py](./settings.py)).

## Installation

Using virtualenv is recommended for installing python requirements. So once activated, run:

```sh
$ pip install -r requirements.txt
```

### External libs

For image processing you will need some extra packages:

- [image manipulation](http://pillow.readthedocs.org/en/latest/installation.html#external-libraries)

### Services

- mongodb
- elasticsearch
- redis
- logstash
- kibana

## CI

Use nosetests for unit tests:

```sh
$ nosetests
```

Behave for behaviour testing:

```sh
$ behave
```

Flake8 for style check:

```sh
$ flake8
```

## Running Dev Server

Use honchu to run the app - it will start api server on port `5000`, websocket server on port `5100` and celery.

```sh
$ honcho start
```

### API Documentation

You can see API Documentation on [apiary](http://docs.superdesk.apiary.io/).

## Running cli commands

```sh
$ python manage.py
```

This will give you list of available commands.

### Creating admin user

This command will create an administrator user.

```sh
$ python manage.py users:create -u <username> -p <password> -e <email> -a
```
