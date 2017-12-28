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

## Requirements

These services must be installed, configured and running:

 * MongoDB
 * ElasticSearch (1.7.x - 2.4.x)
 * Redis
 * Python (>= 3.5)
 * Node.js (with `npm`)

On macOS, if you have [homebrew](https://brew.sh/) installed, simply run: `brew install mongodb elasticsearch@2.4 redis python3 node`.

### General installation steps look like:
```sh
path=~/superdesk
git clone https://github.com/superdesk/superdesk.git $path

# server
cd $path/server
pip install -r requirements.txt
python manage.py app:initialize_data
python manage.py users:create -u admin -p admin -e 'admin@example.com' --admin
honcho start
# if you need some data
python manage.py app:prepopulate

# client
cd $path/client
npm install
grunt server

# open http://localhost:9000 in browser
```

#### :warning:  macOS users

All the above commands need to run inside the Python Virtual Environment, which you can create
using the `pyvenv` command:

- Run `pyvenv ~/pyvenv` to create the files needed to start an environment in the directory `~/pyvenv`.
- Run `. ~/pyvenv/bin/activate` to start the virtual environment in the current terminal session.

Now you may run the installation steps from above.

### Installation on fresh Ubuntu 16.04

```sh
curl -s https://raw.githubusercontent.com/superdesk/fireq/files/superdesk/install | sudo bash
# Open http://<ip_or_domain> in browser
# login: admin
# password: admin
```
More options and details:
- [for users](https://github.com/superdesk/fireq/tree/files/superdesk)
- [for developers](https://github.com/superdesk/fireq/tree/files/superdesk#development)

### Questions and issues

- Our [issue tracker](https://dev.sourcefabric.org/projects/SD) is only for bug reports and feature requests.
- Anything else, such as questions or general feedback, should be posted in the [forum](https://forum.sourcefabric.org/categories/superdesk-dev).

### A special thanks to...

Users, developers and development partners that have contributed to the Superdesk project. Also, to all the other amazing open-source projects that make Superdesk possible!

### License

Superdesk is available under the [AGPL version 3](https://www.gnu.org/licenses/agpl-3.0.html) open source license.
