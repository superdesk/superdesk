# Superdesk Client 
[![Build Status](https://travis-ci.org/superdesk/superdesk-client.png?branch=devel)](https://travis-ci.org/superdesk/superdesk-client)
[![devDependency Status](https://david-dm.org/superdesk/superdesk-client/dev-status.png)](https://david-dm.org/superdesk/superdesk-client#info=devDependencies)
[![Coverage Status](https://coveralls.io/repos/superdesk/superdesk-client/badge.png?branch=devel)](https://coveralls.io/r/superdesk/superdesk-client?branch=devel)

Superdesk Client is a javascript client for Superdesk REST API server.

*License*: [GPLv3](http://www.gnu.org/licenses/gpl-3.0.txt)

*Copyright*: [Sourcefabric o.p.s.](http://www.sourcefabric.org)


## Setup

There are few different ways to run it:

#### a) locally

Client requires `nodejs` installed and a few steps:
```
npm install -g bower grunt-cli
npm install # install other node dependencies
bower install # install bower components
```
After you can start local dev server on port `9000`:
```
grunt server
```

#### b) using Docker
This command will start frontend on localhost:9000.
Change `http://localhost:5000` to an actual backend server:
```
docker build -t superdesk-client:devel ./
docker run -i -p 9000:9000 -t superdesk-client:devel grunt server --server=http://localhost:5000 --force
```

#### c) using Vagrant
Will start frontend on localhost:9000:
```
vagrant up --provider=docker
```

## Running Tests & Code Style Checks
To check the code for syntax and styling issues run the following:

```
$ grunt hint
```

To run the unit tests:
```
$ grunt test
```

To run end-to-end tests:

First in the server folder run:
```
scripts/start_e2e_server.sh
```

Then in the client folder run:
```
$ scripts/test_e2e.sh
```
NOTE: the end-to-end tests might take quite some time to run.

- To run just certain e2e tests replace 'it' with 'fit'


## Info for contributors

### Commit messages

Every commit has to have a meaningful commit message in form:

```
Title
[<empty line>
Description]
[<empty line>
JIRA ref]
```

Where [JIRA ref](https://confluence.atlassian.com/display/FISHEYE/Using+smart+commits) is at least Issue code eg. ```SDUX-13```.

For trivial changes you can ommit JIRA ref or Description or both: ```Fix typo in superdesk.translate docs.```

### CI

You can test your code before sending a PR via: ```grunt ci```

### UI Components Documentation

While running dev server, you can access documentation page on localhost:9000/docs.html. 

Running documentation separately is possible through: ```grunt docs```.
