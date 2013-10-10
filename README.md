# Superdesk REST API Server [![Build Status](https://travis-ci.org/petrjasek/superdesk-server.png?branch=travis-setup)](https://travis-ci.org/petrjasek/superdesk-server)

Superdesk REST API Server is python app on top of mongodb.

## Dependencies

Application requires mongodb running on standard port.

Python version supported are 2.7.5+ and 3.3+.

Using virtualenv is recommended for installing python dependencies.

## Instalation

```sh
$ pip install -r requirements.txt
```

## Unit Testing

```sh
$ nosetests
```

## Behavior Testing

```sh
$ behave
```

## Running Dev Server

```sh
$ python app.py
```

### API Documentation

You can also run server with documentation on ```/docs``` url.

```sh
$ python docs.py
```

## Running cli commands

```sh
$ python manage.py
```

This will give you list of available commands.

### Creating admin user

This command will create an administrator user.

```sh
$ python manage.py users:create -u <username> -p <password>
```
