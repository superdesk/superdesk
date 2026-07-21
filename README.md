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

## Local development (frontend / extension work)

For editing the client or extensions and seeing changes immediately, use
the server-in-Docker / client-native workflow described in
[DEVSETUP.md](./DEVSETUP.md).

### Prerequisites

- **Docker Desktop** installed and running.
- **[Volta](https://volta.sh)** installed (Node version is pinned through it).
- **Sibling repos cloned in the same parent directory as this one**:
  `superdesk-client-core` and `superdesk-planning` are required;
  `superdesk-analytics` and `superdesk-publisher` are optional.

See [DEVSETUP.md#prerequisites](./DEVSETUP.md#prerequisites) for the full
layout diagram and rationale.

### Running it

Once the prerequisites are in place:

1. Run the setup script.
2. Open `http://localhost:9000` and log in with `admin` / `admin`.

There are two ways to drive step 1.

### Option 1 — let Claude Code do it (recommended for new contributors)

If you have Claude Code installed, the project ships four slash commands
that wrap the dev scripts. Open Claude inside this repo and type:

- `/superdesk-setup` — first-time install + link siblings + init DB
- `/superdesk-up` — start the stack day-to-day
- `/superdesk-down` — stop the stack (data preserved)
- `/superdesk-ext list | enable NAME | disable NAME` — toggle in-tree extensions

These are explicit and fast — typing one runs the corresponding script
directly. Use them once you know what you want.

If you don't remember the command name, the
[`superdesk-dev` skill](./.claude/skills/superdesk-dev/SKILL.md) catches
plain-language phrasings ("set up the dev environment", "start
Superdesk", "enable helloWorld"…). It confirms intent with you before
running anything, so the worst case of a misfire is one extra question,
not an unwanted setup.

The project ships a `.claude/settings.json` that pre-approves the dev
scripts, so you won't be asked to approve each Bash command one by one.

### Option 2 — run the scripts directly

```sh
./scripts/dev/setup.sh    # first time
./scripts/dev/up.sh       # daily
./scripts/dev/down.sh     # stop
```

See [DEVSETUP.md](./DEVSETUP.md) for the first-run validation checklist,
flags (`--only`, `--skip`, `--link`, `--reinit`), extension toggling, and
troubleshooting.

## Manual installation

### Requirements

These services must be installed, configured and running:

- MongoDB
- ElasticSearch (7+)
- Redis
- Python (3.12)
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
