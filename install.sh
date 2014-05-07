#!/bin/bash

# setup virtual env
[ ! -f ./env/bin/activate ] && (
    virtualenv -p python3.3 ./env
)
. ./env/bin/activate

# install app
pip install -U pip distribute
pip install -U -r requirements.txt
pip install -U gunicorn

# run
gunicorn -w 4 -b 0.0.0.0:5000 wsgi
