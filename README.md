# Superdesk
[![Test](https://github.com/superdesk/superdesk/actions/workflows/tests.yml/badge.svg)](https://github.com/superdesk/superdesk/actions/workflows/tests.yml)
[![Lint](https://github.com/superdesk/superdesk/actions/workflows/lint.yml/badge.svg)](https://github.com/superdesk/superdesk/actions/workflows/lint.yml)

Superdesk is an open source end-to-end news creation, production, curation,
distribution and publishing platform developed and maintained by Sourcefabric
with the sole purpose of making the best possible software for journalism. It
is scaleable to suit news organizations of any size. See the [Superdesk website](https://www.superdesk.org) for more information.

Looking to stay up to date on the latest news? [Subscribe](http://eepurl.com/bClQlD) to our monthly newsletter.

The Superdesk server provides the API to process all client requests. The client
provides the user interface. Server and client are separate applications using
different technologies.

Find more information about the client configuration in the README file of the repo:
[github.com/superdesk/superdesk-client-core](https://github.com/superdesk/superdesk-client-core)

## Run Superdesk locally using Docker

You can start superdesk using the `docker-compose.yml` file:

```sh
$ docker compose up -d
```

This will start superdesk on http://localhost:8080. On the first run you also have to initialize
elastic/mongo and create a user:

```sh
# Initialize data
$ docker compose exec superdesk-server python manage.py app:initialize_data
# Create first admin user
$ docker compose exec superdesk-server python manage.py users:create -u admin -p admin -e admin@localhost --admin
```

Then you can login with admin:admin credentials.

The Docker images are hosted on Dockerhub for the [client](https://hub.docker.com/r/sourcefabricoss/superdesk-client) and [server](https://hub.docker.com/r/sourcefabricoss/superdesk-server).

## Manual installation

### Requirements

These services must be installed, configured and running:

- MongoDB
- ElasticSearch (7+)
- Redis
- Python (3.8)
- Node.js (with `npm`)

On macOS, if you have [homebrew](https://brew.sh/) installed, simply run: `brew install mongodb elasticsearch redis python3 node`.

### Installation steps:

```sh
path=~/superdesk
git clone https://github.com/superdesk/superdesk.git $path

# server
cd $path/server
pip3 install -r requirements.txt
python3 manage.py app:initialize_data
python3 manage.py users:create -u admin -p admin -e 'admin@example.com' --admin
honcho start
# if you need some data
python manage.py app:prepopulate

# client
cd $path/client
npm install
npm run build
npx grunt server

# open http://localhost:9000 in browser
```

#### :warning: macOS users

All the above commands need to run inside the Python Virtual Environment, which you can create
using the `pyvenv` command:

- Run `pyvenv ~/pyvenv` to create the files needed to start an environment in the directory `~/pyvenv`.
- Run `. ~/pyvenv/bin/activate` to start the virtual environment in the current terminal session.

Now you may run the installation steps from above.

### Questions and issues

- Our [issue tracker](https://dev.sourcefabric.org/projects/SD) is only for bug reports and feature requests.
- Anything else, such as questions or general feedback, should be posted in the [forum](https://forum.sourcefabric.org/categories/superdesk-dev).

### A special thanks to...

Users, developers and development partners that have contributed to the Superdesk project. Also, to all the other amazing open-source projects that make Superdesk possible!

### License

Superdesk is available under the [AGPL version 3](https://www.gnu.org/licenses/agpl-3.0.html) open source license.
