#!/bin/bash

set -e

# setup virtual env
[ ! -f ./env/bin/activate ] && (
    virtualenv -p python3 ./env
)
. ./env/bin/activate

python --version

# install app
pip install -U pip distribute
pip install -U -r requirements.txt
pip install -U gunicorn

# run
python ws.py
python app.py
