## How to run a fully containerize superdesk development environment

Go to your local code folder (here I'm using `~/code`), and clone your fork of superdesk and superdesk-client-core:

```shell
cd ~/code
git clone git@github.com:lnogues/superdesk.git
git clone git@github.com:lnogues/superdesk-client-core.git
git clone git@github.com:lnogues/superdesk-content-api.git
```

Create symlinkis between superdesk-client-core and superdesk-content-api to superdesk

```shell
ln -s ~/code/superdesk-client-core ~/code/superdesk/superdesk-client-core
ln -s ~/code/superdesk-content-api ~/code/superdesk/superdesk-content-api
```

Then run the docker-compose script

```shell
cd ~/code/superdesk
docker-compose -f docker/docker-compose-dev.yml up
```

Once everything is up and running, quit docker (with Ctrl+C) and run:

```shell
cd ~/code/superdesk/docker
docker-compose run superdesk ./scripts/fig_wrapper.sh python3 manage.py users:create -u admin -p admin -e 'admin@example.com' --admin
```

Now, you can re run your docker compose and your local server is up and running

```shell
cd ~/code/superdesk
docker-compose -f docker/docker-compose-dev.yml up
```

## Run e2e server from docker

For this setup, only the end to end server will run in docker.
The client part will run on your local machine.

Assuming you already have a superdesk development environment set up:

```shell
cd ~/code/superdesk
docker-compose -f docker/docker-compose-e2e.yml up
```

Then the client specific setup:

```shell
cd ~/code/superdesk-client-core
npm install
./node_modules/.bin/webdriver-manager update
```

On the dependencies have been installed and `docker-compose-e2e.yml` is running, you can run the tests:

```shell
./node_modules/.bin/protractor protractor.conf.js \
  --stackTrace --verbose \
  --baseUrl 'http://localhost:9000' \
  --params.baseBackendUrl 'http://localhost:5000/api' \
  --params.username 'admin' \
  --params.password 'admin'
```
