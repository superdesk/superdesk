# Superdesk Client 
[![Build Status](https://travis-ci.org/superdesk/superdesk-client.png?branch=master)](https://travis-ci.org/superdesk/superdesk-client)
[![devDependency Status](https://david-dm.org/superdesk/superdesk-client/dev-status.png)](https://david-dm.org/superdesk/superdesk-client#info=devDependencies)

Superdesk Client is a javascript client for Superdesk REST API server.

*License*: [GPLv3](http://www.gnu.org/licenses/gpl-3.0.txt)

*Copyright*: [Sourcefabric o.p.s.](http://www.sourcefabric.org)

## Setup

Client requires `nodejs` installed and a few steps:
```
npm install -g grunt-cli # install grunt
npm install # install other node dependencies
bower install # install bower components
```
After you can start local dev server on port `9000`:
```
grunt server
```

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

You can test your code before sending a PR via: ```./travis_build.sh```

