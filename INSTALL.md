

We gonna use `ubuntu:trusty` as a base.



#### install system-wide dependencies, python3 and the build-time dependencies for c modules

Execute:

```sh
apt-get update && \
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
python3 python3-dev python3-pip python3-lxml \
build-essential libffi-dev git \
libtiff5-dev libjpeg8-dev zlib1g-dev \
libfreetype6-dev liblcms2-dev libwebp-dev \
curl libfontconfig nodejs npm nginx \
&& echo "\ndaemon off;" >> /etc/nginx/nginx.conf \
&& rm /etc/nginx/sites-enabled/default \
&& ln --symbolic /usr/bin/nodejs /usr/bin/node
```




Execute:

```sh
npm -g install grunt-cli bower
```




#### Set the locale

Execute:

```sh
locale-gen en_US.UTF-8
```


Export environment variables:

```sh
export LANG=en_US.UTF-8 \
LANGUAGE=en_US:en \
LC_ALL=en_US.UTF-8
```



#### setup the environment

Copy from the repository dir:

```sh
cp -r ./docker/nginx.conf /etc/nginx/nginx.conf
cp -r ./docker/superdesk_vhost.conf /etc/nginx/sites-enabled/superdesk.conf
cp -r ./docker/start.sh /opt/superdesk/start.sh
```









#### set env vars for the server

Export environment variables:

```sh
export PYTHONUNBUFFERED=1 \
C_FORCE_ROOT="False" \
CELERYBEAT_SCHEDULE_FILENAME=/tmp/celerybeatschedule.db
```



#### install server dependencies

Copy from the repository dir:

```sh
cp -r ./server/requirements.txt /tmp/requirements.txt
```

Execute:

```sh
cd /tmp && pip3 install -U -r /tmp/requirements.txt
```




#### install client dependencies

Copy from the repository dir:

```sh
cp -r ./client/package.json /opt/superdesk/client/
```

Execute:

```sh
cd ./client && npm install
```


Copy from the repository dir:

```sh
cp -r ./client/bower.json /opt/superdesk/client/
cp -r ./client/.bowerrc /opt/superdesk/client/
```

Execute:

```sh
cd ./client && bower --allow-root install
```




#### copy server sources

Copy from the repository dir:

```sh
cp -r ./server /opt/superdesk
```



#### copy client sources

Copy from the repository dir:

```sh
cp -r ./client /opt/superdesk/client
```



#### prebuild client

Execute:

```sh
cd ./client && grunt build
```


-------

Working directory is: `/opt/superdesk/`

To start the application execute:

```sh
/opt/superdesk/start.sh
```

Following ports will be used by the application:

```sh
9000, 80
```

Following ports will be used by the application:

```sh
5000, 5100
```
